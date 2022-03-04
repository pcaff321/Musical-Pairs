from time import process_time
from .models import Experiment, ImageRound, Page, SurveyRound, AudioRound, TextRound, Survey, SurveyQuestion, set_image_name

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
        prime = getVar(string, "prime")
        pairs = getVar(string, "pairs")
        bundleID = getVar(string, "bundleID")
        
        data = {"pairs": pairs, "prime": prime, "bundleID": bundleID}
        
    if roundType == "text":
        text = getVar(string, "text")
        
        data = {"text": text}

    if roundType == "image":
        questionText = getVar(string, "questionText")
        name = getVar(string, "name")
        
        data = {"questionText": questionText, "name": name}
        
    data['roundType'] = roundType
    
    return data


def getQuestions(survey):
    questions = SurveyQuestion.objects.filter(survey=survey).order_by('questionNumber')
    questionList = list()
    for question in questions:
        questionType = str(question.questionType)
        if questionType == '1':
            questionType = 'text'
        elif questionType == '2':
            questionType = 'slider'
        elif questionType == '3':
            questionType = 'yesOrNo'
        questionDict = {"questionText": question.questionText, "questionType": questionType, "id": question.id}
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

def createImageRound(image, experiment, user, questionText, name):
    survey = Survey(name="ImageRoundQuestion", user_source=user)
    survey.save()
    question = SurveyQuestion(user_source=user, survey=survey, questionText=questionText, questionType=1, questionNumber=1)
    question.save()
    imageRound = ImageRound(name=name, experiment=experiment, user_source=user, image=image, survey=survey)
    imageRound.save()
    return imageRound

def createAudioRound(pairs, prime, experiment, user, wordBundle):
    audioRound = AudioRound(pairs=pairs, prime=prime, experiment=experiment, user_source=user, word_bundle=wordBundle)
    audioRound.save()
    return audioRound


def createSurveyQuestion(user, survey, questionText, questionType, questionNumber):
    question = SurveyQuestion(user_source=user, survey=survey, questionText=questionText, questionType=questionType, questionNumber=questionNumber)
    question.save()
    return question

def createSurveyRound(experiment, survey, user):
    surveyRound = SurveyRound(survey=survey, experiment=experiment, user_source=user)
    surveyRound.save()
    return surveyRound