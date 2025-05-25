from flask import Flask, render_template, request, redirect, session, jsonify
import os
from supabase import create_client, Client

app = Flask(__name__)

# Supabase setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials")

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
        if user.data and len(user.data) > 0:
            return jsonify({"balance": user.data[0]["balance"]})
        else:
            return jsonify({"error": "User not found"}), 404
    elif request.method == "POST":
        new_balance = float(request.json["balance"])
        supabase.table("users").update({"balance": new_balance}).eq("name", username).execute()
        return jsonify({"status": "updated"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
