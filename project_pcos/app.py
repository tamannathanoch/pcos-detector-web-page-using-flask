from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import re

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session handling

USER_DATA_FILE = "users.json"

# Load user data from JSON
def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

# Save user data to JSON
def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

@app.route("/")
def home():
    pcos_facts = [
        "PCOS affects 1 in 10 women of reproductive age.",
        "Common symptoms include irregular periods, weight gain, and acne.",
        "It can lead to fertility issues if not managed properly.",
        "Lifestyle changes and medications can help manage PCOS.",
        "Early diagnosis and treatment can prevent long-term complications."
    ]
    return render_template("home.html", pcos_facts=pcos_facts, page="home")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
            return render_template("signup.html", error="Invalid email format. Use @gmail.com.", page="signup")

        users = load_users()

        if email in users:
            return render_template("signup.html", error="Email already exists. Please log in.", page="signup")

        users[email] = {"password": password}
        save_users(users)
        
        session["logged_in"] = True
        session["email"] = email
        return redirect(url_for("quiz_intro"))

    return render_template("signup.html", page="signup")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        if email in users and users[email]["password"] == password:
            session["logged_in"] = True
            session["email"] = email
            return redirect(url_for("quiz_intro"))
        else:
            return render_template("login.html", error="Invalid credentials. Please try again.", page="login")

    return render_template("login.html", page="login")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("email", None)
    return redirect(url_for("home"))

@app.route("/quiz_intro")
def quiz_intro():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    return render_template("quiz_intro.html", page="quiz_intro")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        answers = {
            "Do you experience irregular menstrual cycles?": request.form.get("q1"),
            "Do you notice excessive facial or body hair?": request.form.get("q2"),
            "Have you experienced unexplained weight gain?": request.form.get("q3"),
            "Do you have frequent acne or oily skin?": request.form.get("q4"),
            "Do you have difficulty losing weight despite efforts?": request.form.get("q5")
        }
        
        yes_count = sum(1 for answer in answers.values() if answer == "yes")
        
        if yes_count >= 3:
            result = "Positive"
        elif yes_count == 2:
            result = "Neutral"
        else:
            result = "Negative"

        session['quiz_answers'] = answers
        return redirect(url_for("result", result=result))

    return render_template("quiz.html", page="quiz")

@app.route("/result")
def result():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    
    result = request.args.get("result", "Neutral")
    answers = session.get('quiz_answers', {})
    
    # Risk calculation
    risk_levels = {
        "Positive": "high",
        "Neutral": "moderate", 
        "Negative": "low"
    }
    
    # Recommendations based on result
    recommendations = {
        "Positive": [
            {"icon": "🩺", "text": "Consult a gynecologist for proper diagnosis"},
            {"icon": "🥗", "text": "Start a PCOS-friendly diet plan"},
            {"icon": "🏥", "text": "Consider hormonal tests"}
        ],
        "Neutral": [
            {"icon": "📅", "text": "Track your menstrual cycle regularly"},
            {"icon": "🏃‍♀️", "text": "Increase physical activity"},
            {"icon": "🩸", "text": "Monitor symptoms for changes"}
        ],
        "Negative": [
            {"icon": "👍", "text": "Maintain healthy lifestyle habits"},
            {"icon": "🔍", "text": "Stay aware of PCOS symptoms"},
            {"icon": "📚", "text": "Educate yourself about PCOS"}
        ]
    }
    
    return render_template(
        "result.html",
        result_message=result,
        sentiment=result.lower(),
        risk_level=risk_levels.get(result, "moderate"),
        risk_percentage=80 if result == "Positive" else 50 if result == "Neutral" else 20,
        answers=answers,
        recommendations=recommendations.get(result, []),
        page="result"
    )
@app.route("/recommend")
def recommend():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    return render_template("recommend.html", page="recommend")

@app.route("/blogs")
def blogs():
    return render_template("blogs.html", page="blogs")

@app.route("/podcasts")
def podcasts():
    return render_template("podcasts.html", page="podcasts")

@app.route("/videos")
def videos():
    return render_template("videos.html", page="videos")

@app.route("/articles")
def articles():
    return render_template("articles.html", page="articles")

@app.route("/about")
def about():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    return render_template("about.html", page="about")   

@app.route("/help")
def help():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    return render_template("help.html", page="help")     

if __name__ == "__main__":
    app.run(debug=True)