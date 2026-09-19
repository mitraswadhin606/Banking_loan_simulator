from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "banking-loan-risk-assessment"

VALID_USERS = {
    "admin": "admin123",
    "manager": "manager123",
}


def determine_risk(data):
    age = int(data.get("age", 0))
    monthly_income = float(data.get("monthly_income", 0))
    employment_type = (data.get("employment_type") or "").strip().lower()
    loan_amount = float(data.get("loan_amount", 0))
    credit_score = int(data.get("credit_score", 0))

    score = 0
    reasons = []

    if age >= 21 and age <= 60:
        score += 1
        reasons.append("Applicant age is within the preferred borrowing range.")
    else:
        score -= 1
        reasons.append("Age is outside the preferred borrowing range.")

    if monthly_income >= 80000:
        score += 2
        reasons.append("High monthly income supports repayment capacity.")
    elif monthly_income >= 45000:
        score += 1
        reasons.append("Moderate income supports the request.")
    else:
        score -= 1
        reasons.append("Low monthly income increases repayment risk.")

    if employment_type in {"salaried", "self-employed", "business owner"}:
        score += 1
        reasons.append("Stable employment type reduces risk.")
    else:
        score -= 1
        reasons.append("Employment status is weak for loan repayment.")

    if loan_amount <= monthly_income * 4:
        score += 2
        reasons.append("Loan amount is affordable compared with income.")
    elif loan_amount <= monthly_income * 6:
        score += 1
        reasons.append("Loan amount is moderate relative to income.")
    else:
        score -= 2
        reasons.append("Loan amount is high compared with monthly income.")

    if credit_score >= 700:
        score += 2
        reasons.append("Strong credit score supports low risk.")
    elif credit_score >= 600:
        score += 1
        reasons.append("Credit score is acceptable but not ideal.")
    else:
        score -= 2
        reasons.append("Low credit score raises default risk.")

    if score >= 5:
        risk = "Low Risk"
    elif score >= 2:
        risk = "Medium Risk"
    else:
        risk = "High Risk"

    return risk, reasons[:5]


def get_dashboard_context():
    applications = session.get("applications", [])
    return {
        "username": session.get("username", "User"),
        "stats": {
            "applications": len(applications),
            "approved": sum(application.get("status") == "Approved" for application in applications),
            "pending": 0,
            "disbursed": "₹0",
        },
        "recent_applications": applications[-5:],
    }


@app.route("/")
def index():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if VALID_USERS.get(username) == password:
        session["logged_in"] = True
        session["username"] = username
        flash("Login successful.", "success")
        return redirect(url_for("dashboard"))

    flash("Invalid username or password.", "error")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        flash("Please log in first.", "error")
        return redirect(url_for("index"))
    return render_template("dashboard.html", **get_dashboard_context())


@app.route("/loan_application")
def loan_application():
    if not session.get("logged_in"):
        flash("Please log in first.", "error")
        return redirect(url_for("index"))
    return render_template("loan_application.html", username=session.get("username", "User"))


@app.route("/assessment")
def assessment_view():
    if not session.get("logged_in"):
        flash("Please log in first.", "error")
        return redirect(url_for("index"))

    customer = session.get("last_customer")

    if not customer:
        return render_template(
            "assessment.html",
            username=session.get("username", "User"),
            customer=None,
            risk=None,
            reasons=[],
        )

    risk, reasons = determine_risk({
        "age": customer.get("age", "0"),
        "monthly_income": customer.get("monthly_income", "0"),
        "employment_type": customer.get("employment_type", ""),
        "loan_amount": customer.get("loan_amount", "0"),
        "loan_purpose": customer.get("loan_purpose", ""),
        "credit_score": customer.get("credit_score", "0"),
    })

    return render_template(
        "assessment.html",
        username=session.get("username", "User"),
        customer=customer,
        risk=risk,
        reasons=reasons,
    )


@app.route("/assess", methods=["POST"])
def assess():
    if not session.get("logged_in"):
        flash("Please log in first.", "error")
        return redirect(url_for("index"))

    customer = {
        "name": request.form.get("customer_name", "Customer"),
        "age": request.form.get("age", "0"),
        "monthly_income": request.form.get("monthly_income", "0"),
        "employment_type": request.form.get("employment_type", ""),
        "loan_amount": request.form.get("loan_amount", "0"),
        "loan_purpose": request.form.get("loan_purpose", ""),
        "credit_score": request.form.get("credit_score", "0"),
    }
    session["last_customer"] = customer

    applications = session.get("applications", [])
    risk, _ = determine_risk(customer)
    risk_score = {"Low Risk": 82, "Medium Risk": 60, "High Risk": 35}[risk]
    applications.append({
        "id": f"APP-{len(applications) + 1:03d}",
        "name": customer["name"],
        "loan_amount": f"₹{customer['loan_amount']}",
        "purpose": customer["loan_purpose"],
        "score": risk_score,
        "risk": risk,
        "email": f"{customer['name'].lower().replace(' ', '.')}@example.com",
        "phone": "Not provided",
        "age": customer["age"],
        "income": f"₹{customer['monthly_income']}",
        "employment": customer["employment_type"],
        "credit_score": customer["credit_score"],
        "status": "In Review",
    })
    session["applications"] = applications

    flash("Application submitted successfully.", "success")
    return redirect(url_for("assessment_view"))


@app.route("/applications")
def applications():
    if not session.get("logged_in"):
        flash("Please log in first.", "error")
        return redirect(url_for("index"))
    return render_template(
        "applications.html",
        username=session.get("username", "User"),
        applications=session.get("applications", []),
    )


@app.route("/application_details/<application_id>")
def application_details(application_id):
    if not session.get("logged_in"):
        flash("Please log in first.", "error")
        return redirect(url_for("index"))
    customer = next(
        (application for application in session.get("applications", []) if application["id"] == application_id),
        None,
    )
    if customer is None:
        return render_template("404.html"), 404
    customer = {
        "id": application_id,
        "name": customer.get("name", "Applicant"),
        "email": customer.get("email", "Not provided"),
        "phone": customer.get("phone", "Not provided"),
        "age": customer.get("age", "Not provided"),
        "income": customer.get("income", "Not provided"),
        "employment": customer.get("employment", "Not provided"),
        "loan_amount": customer.get("loan_amount", "Not provided"),
        "purpose": customer.get("purpose", "Not provided"),
        "credit_score": customer.get("credit_score", "Not provided"),
        "risk": customer.get("risk", "Medium Risk"),
        "status": customer.get("status", "In Review"),
        "score": customer.get("score", "Pending"),
    }
    return render_template("application_details.html", username=session.get("username", "User"), customer=customer)


@app.route("/application_status/<application_id>/<status>", methods=["POST"])
def update_application_status(application_id, status):
    if not session.get("logged_in"):
        flash("Please log in first.", "error")
        return redirect(url_for("index"))
    if status not in {"Approved", "Rejected"}:
        return render_template("404.html"), 404

    applications = session.get("applications", [])
    application = next((item for item in applications if item.get("id") == application_id), None)
    if application is None:
        return render_template("404.html"), 404

    application["status"] = status
    session["applications"] = applications
    flash(f"Application {application_id} marked as {status.lower()}.", "success")
    return redirect(url_for("application_details", application_id=application_id))


@app.route("/profile")
def profile():
    if not session.get("logged_in"):
        flash("Please log in first.", "error")
        return redirect(url_for("index"))
    return render_template("profile.html", username=session.get("username", "User"))


@app.route("/settings")
def settings():
    if not session.get("logged_in"):
        flash("Please log in first.", "error")
        return redirect(url_for("index"))
    return render_template("settings.html", username=session.get("username", "User"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
