from flask_wtf import FlaskForm
from wtforms import widgets, StringField, PasswordField, BooleanField, SubmitField, RadioField, IntegerField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app.models import User

CATEGORY_MAP = {
    "1": "【中醫基礎理論】",
    "2": "【中醫經典文獻】",
    "3": "【診斷與辨證學】",
    "4": "【經絡與針灸學】",
    "5": "【中藥本草學】",
    "6": "【中醫內科學】（含婦科兒科神志病）",
    "7": "【中醫外科學】（含皮膚科、傷科）",
    "8": "【中醫五官科學】（含眼耳鼻喉眼）"
}

CAT_LIST = {
    "1": "本類別涵蓋了構成中醫藥學基礎的核心原理、概念和哲學框架。屬於此類別的問題應與中醫的基本理論相關，例如陰陽、五行、藏象學說、氣血津液等。它還包括從中醫角度看人體的基本生理和病理機制，例如氣血的生成與運行，以及人體各臟腑系統之間的相互關係。簡而言之，任何關於中醫藥學基本構成要素和基礎原則的問題都屬於此類別。",
    "2": "本類別專門用於分類與中醫藥古籍、經典著作及其思想體系相關的問題。具體包括但不限於《黃帝內經》、《傷寒雜病論》、《金匱要略》、《溫病條辨》等對後世影響深遠的醫書。此類別的問題通常涉及對這些古籍中理論、病證、方藥、診法等內容的解讀、分析、比較或應用，以及對歷代醫家學術思想源流的探討。簡而言之，任何關於中醫藥歷史文獻、經典著作及其思想體系的問題都歸入此類別。",
    "3": "本類別主要用於分類與中醫診察疾病和辨識證候相關的問題。它涵蓋了中醫的「四診」，即望、聞、問、切，以及如何通過這些方法收集患者資訊。更重要的是，本類別還包括了「辨證論治」的核心思想，例如如何根據四診收集到的資訊，運用八綱辨證、臟腑辨證、氣血津液辨證等方法，來分析、判斷疾病的病位、病性、病勢，從而確定治療原則。簡而言之，任何關於中醫如何診斷疾病、如何分析和歸納證候的問題都屬於此類別。",
    "4": "本類別專門用於分類與中醫經絡系統和針灸治療技術相關的問題。它涵蓋了經絡的循行路線、生理功能、病理表現、經穴的定位與主治。此外，所有關於針刺、艾灸、拔罐、推拿等以經絡和穴位為基礎的治療方法，以及這些療法在臨床中的具體應用、操作技巧、注意事項和理論機制，都屬於此類別。簡而言之，任何關於經絡、腧穴和針灸治療方法的問題都歸入此類別。",
    "5": "本類別主要用於分類與中草藥、方劑配伍及其應用相關的問題。它涵蓋了對單個中藥的性味、歸經、功效、主治、用法用量和禁忌的討論。此外，本類別還包括如何將不同的藥物組合成方劑，討論方劑的組成原則（如君臣佐使）、配伍變化、煎煮方法以及方劑在臨床中的具體應用。簡而言之，任何關於中草藥、成藥、方劑和本草理論的問題都屬於此類別。",
    "6": "本類別涵蓋了中醫藥在內科常見病、多發病以及婦科、兒科和神志疾病方面的臨床診治問題。它包括對各種病證的辨證論治，如感冒、咳嗽、胃痛、眩暈等內科疾病；月經不調、痛經、妊娠病、不孕症等婦科疾病；小兒發熱、疳積、驚風等兒科疾病；以及失眠、抑鬱、焦慮等神志疾病。任何關於使用中藥方劑、針灸或其他療法來治療這些具體疾病的臨床應用、病因病機、症狀特點和治療方案的問題，都應歸入此類別。",
    "7": "本類別主要用於分類與中醫藥在外科、皮膚科和傷科疾病方面的診療問題。它涵蓋了瘡瘍、癰疽、瘰癧、乳腺病等外科疾病，以及濕疹、痤瘡、銀屑病等皮膚病。此外，所有關於跌打損傷、骨折、脫臼、筋傷等外傷疾病的診斷、治療和康復，以及使用外用藥膏、敷貼、正骨手法等治療方法的問題，都應歸入此類別。簡而言之，任何關於中醫治療體表疾病、外傷和皮膚問題的臨床應用，都屬於此類別。",
    "8": "本類別專門用於分類與中醫眼、耳、鼻、喉等五官疾病的診治相關的問題。它涵蓋了眼部疾病（如結膜炎、白內障）、耳部疾病（如耳鳴、耳聾）、鼻部疾病（如鼻炎、鼻竇炎）和咽喉疾病（如扁桃體炎、咽炎）的病因病機、辨證論治、方藥選擇以及針灸、推拿等治療方法。簡而言之，任何關於中醫藥如何診斷和治療眼、耳、鼻、喉等五官系統疾病的臨床問題都屬於此類別。"
}

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=(DataRequired(), Email()))
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', 
                validators=(DataRequired(), EqualTo('password')))
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already exists.')



# class QuestionForm(FlaskForm):
#     # category = SelectMultipleField('請選擇下一個類別', choices=CATEGORY_MAP, validators=[DataRequired()])
#     difficulty = IntegerField('请选择问题难度（1至5之间）', validators=[DataRequired(), NumberRange(min=1, max=5, message="请选择问题难度（1至5之间")])
#     submit = SubmitField('提交並繼續', validators=[DataRequired()])

class QuestionForm(FlaskForm):
    # This field will handle both single and multiple-choice questions
    # by using RadioField for single and a List for multiple.
    options = SelectMultipleField('Options', validators=[DataRequired()])
    
    # This field handles the categories.
    category = SelectMultipleField('Category', validators=[DataRequired()])
    
    # This field handles the difficulty, ensuring it's an integer between 1 and 5.
    difficulty = IntegerField('Difficulty', validators=[DataRequired(), NumberRange(min=1, max=5)])
    
    submit = SubmitField('下一个')