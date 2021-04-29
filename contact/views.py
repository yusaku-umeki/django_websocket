import json

from django.contrib.auth.hashers import check_password, make_password
from django.core import mail, serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.signing import BadSignature
from django.http import Http404, HttpResponse, JsonResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, FormView, ListView, TemplateView, View

from .forms import ChatPasswordForm, ContactForm, ResetPasswordForm
from .models import Chat, ChatThread, Member, News
from .signing import dumps, loads


class ContactView(FormView):
    template_name = "main/contact.html"
    form_class = ContactForm
    success_url = "/contact_complete"

    def form_valid(self, form):
        if form.cleaned_data["password"]:
            password = make_password(form.cleaned_data["password"])
        else:
            password = None
        thread = ChatThread.objects.create(
            username=form.cleaned_data["username"],
            group=form.cleaned_data["group"],
            email=form.cleaned_data["email"],
            phone_number=form.cleaned_data["phone_number"],
            category=form.cleaned_data["category"],
            password=password,
        )
        Chat.objects.create(thread=thread, content=form.cleaned_data["content"])
        token = dumps({"pk": thread.pk, "email": thread.email})
        params = {
            "thread": thread,
            "scheme": self.request.scheme,
            "host": self.request.get_host(),
            "url": reverse("main:chat", args=[token]),
            "content": form.cleaned_data["content"],
            "get_category_display": dict(thread.CategoryChoices.choices)[int(thread.category)],
        }
        email_to_user = mail.EmailMessage(
            "【株式会社DeMiA】お問合せありがとうございます",
            render_to_string("main/email/contact_reply_to_user.txt", params),
            "hp_form@demia.co.jp",
            [thread.email],
        )

        params["url"] = reverse("admin:main_chatthread_change", args=[thread.id])

        email_to_staff = mail.EmailMessage(
            "【株式会社DeMiA】お問合が来ました",
            render_to_string("main/email/contact_reply_to_staff.txt", params),
            "hp_form@demia.co.jp",
            ["info@demia.co.jp"],
        )

        connection = mail.get_connection()
        connection.open()
        connection.send_messages([email_to_user, email_to_staff])
        connection.close()

        return redirect(reverse("main:chat", args=[token]))

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()
        return initial


class ThreadInboxView(ListView):
    template_name = "main/chat/thread_list.html"
    model = ChatThread
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_staff:
            self.queryset = ChatThread.objects.select_related("staff").prefetch_related("chat_set")
        else:
            token = self.kwargs["token"]
            loaded_token = loads(token)
            email = loaded_token["email"]
            self.queryset = ChatThread.objects.filter(email=email).prefetch_related("chat_set")
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token_dict = {}
        for thread in self.queryset:
            token = dumps({"pk": thread.pk, "email": thread.email})
            token_dict[thread.pk] = token

        context.update(
            {
                "token_dict": token_dict,
            }
        )

        return context


class ChatView(TemplateView):
    template_name = "main/chat/room.html"

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        token = self.kwargs["token"]
        try:
            obj = loads(token)
            self.thread = ChatThread.objects.get(pk=obj["pk"], email=obj["email"])
            if self.thread.password and request.session.get("token") != token:
                return redirect(reverse("main:check_thread_password", args=[token]))

        except (BadSignature, KeyError, ChatThread.DoesNotExist) as e:
            return HttpResponseBadRequest(e)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        thread_json = serializers.serialize("json", [self.thread])
        user = self.request.user
        if user.is_staff:
            user_is_staff = True
        else:
            user_is_staff = False
        context = super().get_context_data(**kwargs)
        context.update(
            thread=self.thread,
            thread_json=thread_json,
            user_is_staff=user_is_staff,
            chat_qs=self.thread.chat_set.order_by("id"),
        )
        return context
