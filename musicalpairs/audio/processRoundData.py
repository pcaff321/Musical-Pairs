from .models import Experiment, Page, SurveyExample, AudioRound, TextRound, Survey


def getVar(string, varName):
    _, _, a = string.partition("${}=".format(varName))
    value, _, _ = a.partition("$END")
    return value

def processRound(string):
    data = {}
    roundType = getVar(string, "type")

    if roundType == "experiment":
        experimentID = getVar(string, "experimentID")
        
        data = {"experimentID": experimentID}
    
    if roundType == "survey":
        text = getVar(string, "text")
        surveyID = getVar(string, "surveyID")
        
        data = {"text": text, "surveyID": surveyID}
        
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

def createSurveyRound(text, experiment, surveyID, user):
    survey = Survey.objects.all()[0] # Survey.objects.filter(id=surveyID)[0]
    surveyRound = SurveyExample(text=text, experiment=experiment, survey=survey, user_source=user)
    surveyRound.save()
    return surveyRound