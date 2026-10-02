from django import forms
from django.forms import inlineformset_factory

from normativ.models import Normativ, NormativAnswer, NormativQuestion


class NormativForm(forms.ModelForm):
    class Meta:
        model = Normativ
        fields = ['title', 'description']


class NormativQuestionForm(forms.ModelForm):
    class Meta:
        model = NormativQuestion
        fields = ['text', 'max_score', 'order']


NormativQuestionFormSet = inlineformset_factory(
    Normativ,
    NormativQuestion,
    form=NormativQuestionForm,
    extra=1,
    can_delete=True,
)


class AnswerSubmitForm(forms.Form):
    def __init__(self, *args, questions=None, existing=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = list(questions or [])
        existing = existing or {}
        for question in self.questions:
            field_name = f'answer_{question.pk}'
            prior = existing.get(question.pk)
            self.fields[field_name] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 3}),
                required=prior is None,
                label=f'{question.order}. {question.text}',
                initial=prior.answer_text if prior else '',
                disabled=prior is not None,
            )

    def cleaned_answers(self):
        result = {}
        for question in self.questions:
            field_name = f'answer_{question.pk}'
            if field_name in self.cleaned_data and not self.fields[field_name].disabled:
                result[question] = self.cleaned_data[field_name]
        return result


class GradeForm(forms.Form):
    def __init__(self, *args, answers=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.answers = list(answers or [])
        for answer in self.answers:
            score_name = f'score_{answer.pk}'
            feedback_name = f'feedback_{answer.pk}'
            self.fields[score_name] = forms.IntegerField(
                min_value=0,
                max_value=answer.question.max_score,
                initial=answer.score,
                label=f'Ball (0-{answer.question.max_score})',
                required=True,
            )
            self.fields[feedback_name] = forms.CharField(
                required=False,
                initial=answer.feedback,
                label='Izoh',
                widget=forms.TextInput(),
            )

    def cleaned_grades(self):
        result = []
        for answer in self.answers:
            result.append({
                'answer': answer,
                'score': self.cleaned_data[f'score_{answer.pk}'],
                'feedback': self.cleaned_data[f'feedback_{answer.pk}'],
            })
        return result
