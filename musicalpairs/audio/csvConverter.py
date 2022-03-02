""" import csv


def getGuessesBasedOnPrime(experiment, prime):
    pairGuessesQuery = UserPairGuess.objects.filter(prime=prime)
    pairGuesses = list()
    for guess in pairGuessesQuery:
        if guess.associated_word_round.experiment == experiment:
            pairGuesses.append(guess)
    return pairGuesses


def getChartData(guesses):
    correct = 0
    total = len(guesses)
    for guess in guesses:
        pair = guess.pair
        word1 = pair.audio1.word
        word2 = pair.audio2.word
        answer = guess.answer
        if word2.lower() == answer.lower():
            correct += 1
    scoresData = [correct, (total-correct)]
    labels = ["Correct", "Incorrect"]
    percent = 0.0
    if total > 0:
        percent = round((correct / total) * 100, 2)

    return scoresData, labels, percent

header = ['USER ID', 'WORD ONE', 'WORD TWO', 'GUESS', 'PRIME']
data = ['3', 'BEEF', 'BIRD', 'POO', 'J']


def makeCSVforAudiodRound(audio_round):
    pairGuessesQuery = UserPairGuess.objects.all()
    researcher_id = audio_round.user_source.id
    pairGuesses = list()
    for guessQuery in pairGuessesQuery:
        if guessQuery.associated_word_round.associated_audio_round == audio_round:
            pairGuesses.append(guessQuery)
    data = list()
    for guess in pairGuesses:
        pair = guess.pair
        word1 = pair.audio1.word
        word2 = pair.audio2.word
        answer = guess.answer
        userID = guess.associated_word_round.for_user.id
        prime = guess.prime
        pairList = [userID, word1.lower(), word2.lower(), answer.lower(), prime]
        data.append(pairList)
    
    fileName = settings.MEDIA_URL + "/" + str(researcher_id) + "/" + "AudioRound" + str(audio_round.id)
    with open(fileName, 'w', encoding='UTF8', newline='') as f:

        writer = csv.writer(f)

        writer.writerow(header)

        writer.writerow(data)



with open('countries.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write the data
    writer.writerow(data) """