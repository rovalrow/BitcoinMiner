from flask import Flask, render_template, request, redirect, session, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

# Supabase setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        result = supabase.table("users").select("*").eq("name", username).eq("password", password).execute()
        if result.data:
            session["user"] = username
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    return render_template("login.html")

@app.route("/miner")
def miner():
    if "user" not in session:
        return redirect("/")
    return render_template("miner.html", username=session["user"])

@app.route("/balance", methods=["GET", "POST"])
def balance():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 403
    username = session["user"]
    if request.method == "GET":
        user = supabase.table("users").select("balance").eq("name", username).execute()
        if user.data:
            return jsonify({"balance": user.data[0]["balance"]})
        return jsonify({"balance": 0})
    elif request.method == "POST":
        new_balance = float(request.json["balance"])
        supabase.table("users").update({"balance": new_balance}).eq("name", username).execute()
        return jsonify({"status": "updated"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
