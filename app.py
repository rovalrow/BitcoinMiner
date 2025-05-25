from flask import Flask, render_template, request, redirect, session, jsonify
import os
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

# Supabase setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        data = supabase.table("users").select("*").eq("name", username).eq("password", password).execute()
        if data.data:
            session["user"] = username
            return redirect("/miner")
        else:
            return render_template("login.html", error="Invalid credentials.")
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
        return jsonify({"balance": user.data[0]["balance"]})
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
