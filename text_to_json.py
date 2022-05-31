import json

#создаём файл json из текстового файла
cenz = []

with open('spisok.txt', encoding="utf-8") as ar:
    for i in ar:
        s = i.lower().split('\n')[0]
        if s!= '':
           cenz.append(s)


with open('spisok.json', 'w', encoding="utf-8") as e:
    json.dump(cenz, e)

    
