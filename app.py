from bson.int64 import Int64
from bson import json_util, ObjectId
from pymongo import MongoClient, CursorType, ASCENDING, DESCENDING
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
import requests
import json
import re

app = Flask(__name__)


# DB links for pokedexDB collection
client = MongoClient("mongodb://localhost:27017")
database = client["local"]
collection = database["pokedexDB"]


def getAllPokemons():
    # Fetches all Pokemons & sends only things which are most important
    apiPok = "https://5n6ugc33m6.execute-api.us-east-1.amazonaws.com/api/pokedex"
    r = requests.get(
        url=apiPok)
    json_data = json.loads(r.text)

    final_json_data = list()
    for j in json_data:
        t = dict()
        t["name"] = j["name"]
        t["id"] = j["id"]
        final_json_data.append(t)
    return final_json_data


def createNewCategoryInDB():
    # Get last category number
    results = collection.find({})
    for k in results[0]["data"]["new"].keys():
        cat = k
    cat = [int(s) for s in re.findall(r'-?\d+\.?\d*', cat)][0]

    # Update collection
    collection.update_one(
        {"user": "user1"},
        {"$set": {f"data.new.category{cat+1}": []}}
    )


@app.route('/')
def index():
    r = getAllPokemons()
    # return render_template('index.html', things=things)
    return jsonify(r)


@app.route('/createNewCategory', methods=['POST'])
def createNewCategory():
    createNewCategoryInDB()
    # return render_template('index.html', things=things)
    return jsonify("success")


@app.route('/addToCategory', methods=['GET', 'POST'])
def addToCategory():
    # This method adds list for new Categories
    # & copies old items in old section

    if request.method == 'GET':
        return render_template("addToCat.html")

    # Receiving data
    user = request.values.get('userx')
    category = request.values.get('categoryx')
    categoryItems = request.values.getlist('categoryItems[]')

    # Transfering categories from `new` to `old` f"user.data.new.{category}"
    result = collection.find({"user": user})
    for res in result:
        old_cat_extracted = res["data"]["new"][category]
        break

    # Updating old record
    collection.update_one(
        {"user": user},
        {"$set": {f"data.old.{category}": old_cat_extracted}}
    )

    # Adding to specific category of DB
    collection.update_one(
        {"user": user},
        {"$set": {f"data.new.{category}": categoryItems}}
    )

    print(user, category, categoryItems)
    # return render_template('index.html', things=things)
    return jsonify(user, category, categoryItems)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
