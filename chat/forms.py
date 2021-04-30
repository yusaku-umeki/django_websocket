from django import forms

from .models import Chat, ChatThread


class ContactForm(forms.Form):
    group = forms.CharField(required=False, label="団体名（学生の方はご所属）", max_length=50)
    username = forms.CharField(label="お名前", max_length=50)
    phone_number = forms.CharField(required=False, label="お電話番号", max_length=20)
    email = forms.EmailField(label="メールアドレス", max_length=100)
    category = forms.ChoiceField(
        choices=ChatThread.CategoryChoices.choices, label="ご用件（タブからお選びください）"
    )
    content = forms.CharField(widget=forms.Textarea(), label="お問い合わせ内容", max_length=1000)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "class_name"}),
        min_length=4,
        max_length=4,
        required=False,
        label="パスワード（必須ではありません）",
    )


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ("content", "src")
