import pymongo
client = pymongo.MongoClient(host='127.0.0.1', port=27017)
db = client['cidufanyi']
col = db['fanyi']
results = col.find()
with open('output.txt', 'a') as f:
    for result in results:
        f.write(result['enSen'] + '\n' + result['cnSen'] + '\n')
