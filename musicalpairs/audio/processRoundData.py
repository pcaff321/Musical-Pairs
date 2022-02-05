from .models import Experiment, Page, SurveyRound, AudioRound, TextRound, Survey, SurveyQuestion

## EXAMPLE STRING:
experimentInfo = "$type=experiment$END$experimentID=TestExperiment123$END"

surveyRound = "$type=survey$END$text=This Is Survey Text$END$surveyID=je02934jf$END"

textRound = "$type=text$END$text=This is text for a text round$END"

audioRound = "$type=audio$END$add_mumbles=true$END$pairs=5$END$placebo=false$END"

experimentString = "@@@OBJECT-DELIM@@@" + experimentInfo + "@@@OBJECT-DELIM@@@" + textRound + "@@@OBJECT-DELIM@@@" + surveyRound + "@@@OBJECT-DELIM@@@" + audioRound

## Each 'representation' is delimited using @@@OBJECT-DELIM@@@, then processed when received in a post request  



def getVar(string, varName):
    _, _, a = string.partition("${}=".format(varName))
    value, _, _ = a.partition("$END")
    return value

def processRound(string):
    data = {}
    roundType = getVar(string, "type")

    if roundType == "experiment":
        experimentID = getVar(string, "experimentName")
        
        data = {"experimentName": experimentID}
    
    if roundType == "survey":
        name = getVar(string, "name")
        questionsSplit = string.split('@@@QUESTION@@@')
        questions = list()

        for question in questionsSplit:
            if getVar(question, "questionType") != '':
                questionText = getVar(question, "questionText")
                questionType = getVar(question, "questionType")
                if questionType == 'input':
                    questionType = 1
                elif questionType == 'slider':
                    questionType = 2
                elif questionType == 'yesOrNo':
                    questionType = 3
                question = {"questionText": questionText, "questionType": questionType}
                questions.append(question)




        
        data = {"name": "Survey", "questions": questions}
        
    if roundType == "audio":
        mumbles = getVar(string, "add_mumbles")
        pairs = getVar(string, "pairs")
        placebo = getVar(string, "pairs")
        
        data = {"mumbles": mumbles, "pairs": pairs, "placebo": placebo}
        
    if roundType == "text":
        text = getVar(string, "text")
        
        data = {"text": text}
        
    data['roundType'] = roundType
    
    return data


def getQuestions(survey):
    questions = SurveyQuestion.objects.filter(survey=survey)
    questionList = list()
    for question in questions:
        questionType = str(question.questionType)
        if questionType == '1':
            questionType = 'text'
        elif questionType == '2':
            questionType = 'slider'
        elif questionType == '3':
            questionType = 'yesOrNo'
        questionDict = {"questionText": question.questionText, "questionType": questionType}
        questionList.append(questionDict)
    
    return questionList





def createPage(experiment, page_num, content_object, user):
    new_page = Page(page_number=page_num, experiment=experiment, content_object=content_object, user_source=user)
    new_page.save()
    return new_page


def createTextRound(text, experiment, user):
    textRound = TextRound(text=text, experiment=experiment, user_source=user)
    textRound.save()
    return textRound

def createAudioRound(mumbles, pairs, placebo, experiment, user):
    audioRound = AudioRound(mumbles=mumbles, pairs=pairs, placebo=placebo, experiment=experiment, user_source=user)
    audioRound.save()
    return audioRound

    user_source = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    questionText = models.CharField(max_length=3000, null=False)
    questionType = models.PositiveSmallIntegerField(choices=questionTypes, default=1)
    questionNumber

def createSurveyQuestion(user, survey, questionText, questionType, questionNumber):
    question = SurveyQuestion(user_source=user, survey=survey, questionText=questionText, questionType=questionType, questionNumber=questionNumber)
    question.save()
    return question

def createSurveyRound(experiment, survey, user):
    surveyRound = SurveyRound(survey=survey, experiment=experiment, user_source=user)
    surveyRound.save()
    return surveyRound