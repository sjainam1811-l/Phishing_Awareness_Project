
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import sqlite3
import json
from datetime import datetime
from html import escape

# =====================================================
# CONFIGURATION
# =====================================================

HOST = "127.0.0.1"
PORT = 8080
DB = "campaign.db"


# =====================================================
# DATABASE
# =====================================================

def initialize():
    with sqlite3.connect(DB) as con:

        con.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT NOT NULL,
                created TEXT NOT NULL
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS survey_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                noticed_red_flags TEXT NOT NULL,
                next_action TEXT NOT NULL,
                confidence TEXT NOT NULL,
                consent INTEGER NOT NULL,
                created TEXT NOT NULL
            )
        """)


def record(event):
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO events (event, created) VALUES (?, ?)",
            (event, datetime.now().isoformat(timespec="seconds"))
        )


def counts():
    with sqlite3.connect(DB) as con:
        rows = con.execute(
            "SELECT event, COUNT(*) FROM events GROUP BY event"
        ).fetchall()

    result = {name: number for name, number in rows}

    return {
        "email_views": result.get("email_view", 0),
        "clicks": result.get("click", 0),
        "page_views": result.get("page_view", 0),
        "submissions": result.get("demo_submit", 0),
        "reports": result.get("reported", 0)
    }


# =====================================================
# DESIGN AND COMMON LAYOUT
# =====================================================

STYLE = """
<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    color: #172033;
}

header {
    background: #14243b;
    color: white;
    padding: 22px 7%;
}

header h1 {
    margin: 0;
    font-size: 23px;
}

nav {
    margin-top: 15px;
    display: flex;
    flex-wrap: wrap;
    gap: 17px;
}

nav a {
    color: white;
    text-decoration: none;
    font-size: 14px;
}

nav a:hover {
    text-decoration: underline;
}

.container {
    max-width: 1050px;
    margin: 35px auto;
    padding: 20px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 3px 15px #0000000b;
}

h2 {
    margin-top: 0;
}

h3 {
    margin-bottom: 8px;
}

p, li {
    line-height: 1.65;
}

.muted {
    color: #64748b;
    line-height: 1.6;
}

.btn {
    display: inline-block;
    background: #2563eb;
    color: white;
    padding: 12px 19px;
    border: 0;
    border-radius: 7px;
    text-decoration: none;
    cursor: pointer;
    font-size: 15px;
    margin: 4px 2px;
}

.btn:hover {
    background: #1d4ed8;
}

.warning {
    background: #fff7ed;
    color: #9a3412;
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
    line-height: 1.6;
}

.success {
    background: #ecfdf5;
    color: #047857;
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 15px;
}

.stat {
    background: #eff6ff;
    padding: 20px;
    border-radius: 9px;
}

.stat strong {
    display: block;
    font-size: 30px;
    color: #1d4ed8;
}

input:not([type=radio]):not([type=checkbox]) {
    display: block;
    width: 100%;
    padding: 12px;
    margin: 12px 0;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
}

input[type=radio],
input[type=checkbox] {
    display: inline-block;
    width: auto;
    margin: 8px;
}

label {
    line-height: 1.8;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

td, th {
    padding: 12px;
    border-bottom: 1px solid #e2e8f0;
    text-align: left;
}

footer {
    text-align: center;
    color: #64748b;
    padding: 25px;
}

hr {
    border: 0;
    border-top: 1px solid #e2e8f0;
    margin: 20px 0;
}

@media(max-width:600px) {
    .container {
        padding: 12px;
        margin: 15px auto;
    }

    .card {
        padding: 18px;
    }
}
</style>
"""


def layout(title, content):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
{STYLE}
</head>
<body>

<header>
<h1>CyberSafe | Phishing Awareness Lab</h1>

<nav>
<a href="/">Dashboard</a>
<a href="/email">Email Simulation</a>
<a href="/landing">Demo Login</a>
<a href="/stats">Statistics</a>
<a href="/awareness">Awareness Guide</a>
<a href="/survey">Anonymous Survey</a>
<a href="/survey-results">Survey Results</a>
</nav>
</header>

<main class="container">
{content}
</main>

<footer>
Educational Cybersecurity Project | Local Simulation Only
</footer>

</body>
</html>"""


# =====================================================
# 1. DASHBOARD
# =====================================================

def dashboard():

    s = counts()

    content = f"""
    <div class="card">

    <h2>Phishing Awareness Simulation</h2>

    <p class="muted">
    CyberSafe is an educational cybersecurity project
    demonstrating how phishing emails and fraudulent
    login pages can influence user behaviour.
    </p>

    <div class="warning">
    TRAINING ENVIRONMENT:
    No real emails are sent and no passwords or
    personal credentials are collected.
    </div>

    <a class="btn" href="/email">View Sample Email</a>
    <a class="btn" href="/awareness">Learn About Phishing</a>
    <a class="btn" href="/stats">View Statistics</a>

    </div>

    <div class="card">

    <h2>Campaign Overview</h2>

    <div class="grid">

    <div class="stat">
    <strong>{s['email_views']}</strong>
    Email Views
    </div>

    <div class="stat">
    <strong>{s['clicks']}</strong>
    Link Clicks
    </div>

    <div class="stat">
    <strong>{s['page_views']}</strong>
    Landing Page Visits
    </div>

    <div class="stat">
    <strong>{s['submissions']}</strong>
    Demo Attempts
    </div>

    <div class="stat">
    <strong>{s['reports']}</strong>
    Reports
    </div>

    </div>
    </div>

    <div class="card">

    <h2>Project Workflow</h2>

    <ol>
    <li>View the sample phishing email.</li>
    <li>Click the demonstration link.</li>
    <li>View the harmless login demonstration.</li>
    <li>Submit the demo form using dummy information.</li>
    <li>Use the report action to record a report.</li>
    <li>Study phishing awareness information.</li>
    <li>Complete the voluntary anonymous survey.</li>
    <li>Review campaign and survey statistics.</li>
    </ol>

    </div>
    """

    return layout("CyberSafe Dashboard", content)


# =====================================================
# 2. SAMPLE EMAIL SIMULATION
# =====================================================

def email_page():

    record("email_view")

    content = """
    <div class="card">

    <h2>Sample Email Simulation</h2>

    <p class="muted">
    From: Security Awareness Team
    &lt;security@example.test&gt;
    </p>

    <p>
    <b>
    Subject: Action Required – Review Your Account Security
    </b>
    </p>

    <hr>

    <p>Hello User,</p>

    <p>
    Our sample security exercise asks you to review an
    account-security notification.
    </p>

    <p>
    Please use the demonstration link below to see how a
    suspicious email may direct a user to a login page.
    </p>

    <p>
    <a class="btn" href="/click">
    Review Account (Simulation)
    </a>
    </p>

    <p>
    Regards,<br>
    Security Awareness Team
    </p>

    <div class="warning">
    This is a locally displayed educational email preview.
    It has not been sent to anyone.
    </div>

    <hr>

    <p>
    Recognised this as suspicious?
    </p>

    <a class="btn" href="/report">
    Report Suspicious Email
    </a>

    </div>
    """

    return layout("Sample Email", content)


# =====================================================
# 3. DEMONSTRATION LOGIN PAGE
# =====================================================

def landing_page():

    record("page_view")

    content = """
    <div class="card" style="max-width:480px;margin:auto">

    <h2 style="text-align:center">
    Account Verification
    </h2>

    <p class="muted" style="text-align:center">
    Demonstration login interface for cybersecurity education.
    </p>

    <div class="warning">
    This is a fake training page.
    Never enter real credentials.
    </div>

    <form id="demoForm">

    <label>Demo Username</label>

    <input
    type="text"
    placeholder="Enter dummy username"
    autocomplete="off"
    >

    <label>Demo Password</label>

    <input
    type="password"
    placeholder="Dummy password only"
    autocomplete="off"
    >

    <button class="btn" type="submit">
    Continue
    </button>

    </form>

    <p id="message" class="muted"></p>

    </div>

    <script>
    document.getElementById("demoForm").addEventListener(
      "submit", async function(e) {

        e.preventDefault();

        await fetch("/submit", {method:"POST"});

        document.getElementById("message").innerHTML =
          "<b>Training complete!</b> This was a simulated login page. " +
          "No username or password was transmitted or stored.";

        this.reset();
      }
    );
    </script>
    """

    return layout("Login Demonstration", content)


# =====================================================
# 4. CAMPAIGN STATISTICS
# =====================================================

def stats_page():

    s = counts()

    content = f"""
    <div class="card">

    <h2>Campaign Statistics</h2>

    <p class="muted">
    Live counts from this local demonstration.
    </p>

    <table>

    <tr>
    <th>Activity</th>
    <th>Count</th>
    </tr>

    <tr>
    <td>Email preview views</td>
    <td>{s['email_views']}</td>
    </tr>

    <tr>
    <td>Simulation link clicks</td>
    <td>{s['clicks']}</td>
    </tr>

    <tr>
    <td>Landing page visits</td>
    <td>{s['page_views']}</td>
    </tr>

    <tr>
    <td>Demo form attempts</td>
    <td>{s['submissions']}</td>
    </tr>

    <tr>
    <td>Suspicious email reports</td>
    <td>{s['reports']}</td>
    </tr>

    </table>

    <p class="muted">
    These counters record local application activity.
    They do not represent external participants.
    </p>

    <a class="btn" href="/stats">Refresh Statistics</a>
    <a class="btn" href="/">Dashboard</a>

    </div>
    """

    return layout("Campaign Statistics", content)


# =====================================================
# 5. REPORT ACTION
# =====================================================

def report_page():

    content = """
    <div class="card">

    <div class="success">
    <h2>Report Recorded</h2>
    Your training report action was recorded.
    </div>

    <p>
    Reporting suspicious messages is an important
    cybersecurity practice.
    </p>

    <a class="btn" href="/">Return to Dashboard</a>

    </div>
    """

    return layout("Report Simulation", content)


# =====================================================
# 6. PHISHING AWARENESS AND RESEARCH GUIDE
# =====================================================

def awareness_page():

    content = """
    <div class="card">

    <h2>Phishing Awareness Guide</h2>

    <p class="muted">
    Phishing is a social engineering technique in which
    attackers impersonate trusted sources to trick people
    into revealing information or taking unsafe actions.
    </p>

    </div>

    <div class="card">

    <h2>Common Phishing Techniques</h2>

    <h3>1. Email Phishing</h3>

    <p>
    Fraudulent emails imitate trusted organisations and
    encourage users to click links, open attachments or
    disclose confidential information.
    </p>

    <h3>2. Spear Phishing</h3>

    <p>
    Targeted phishing messages are customised for a
    particular individual or organisation.
    </p>

    <h3>3. Website Spoofing</h3>

    <p>
    Fake websites imitate genuine login pages to trick
    visitors into trusting a fraudulent website.
    </p>

    <h3>4. Smishing</h3>

    <p>
    Smishing is phishing conducted through SMS or
    text messages.
    </p>

    <h3>5. Vishing</h3>

    <p>
    Vishing uses fraudulent voice calls to manipulate
    victims into sharing confidential information.
    </p>

    <h3>6. Whaling</h3>

    <p>
    Whaling is a targeted phishing attack aimed at
    senior executives or other high-value individuals.
    </p>

    </div>

    <div class="card">

    <h2>Warning Signs of Phishing</h2>

    <ul>
    <li>Urgent or threatening language.</li>
    <li>Unexpected password reset requests.</li>
    <li>Unknown or suspicious sender addresses.</li>
    <li>Misspelled domain names and unusual URLs.</li>
    <li>Unexpected attachments.</li>
    <li>Requests for passwords or OTPs.</li>
    <li>Unexpected requests for financial information.</li>
    </ul>

    </div>

    <div class="card">

    <h2>Social Engineering Techniques</h2>

    <ul>
    <li><b>Urgency:</b> Creating pressure to act immediately.</li>
    <li><b>Fear:</b> Threatening account suspension or loss.</li>
    <li><b>Authority:</b> Impersonating a trusted organisation.</li>
    <li><b>Curiosity:</b> Using attractive or unexpected content.</li>
    <li><b>Trust:</b> Pretending to be a known person or service.</li>
    </ul>

    </div>

    <div class="card">

    <h2>Preventive Measures</h2>

    <ul>
    <li>Verify the sender before responding.</li>
    <li>Check website addresses carefully.</li>
    <li>Never share passwords or OTPs.</li>
    <li>Enable multi-factor authentication.</li>
    <li>Use a password manager.</li>
    <li>Keep operating systems and software updated.</li>
    <li>Report suspicious messages.</li>
    <li>Participate in cybersecurity awareness training.</li>
    </ul>

    </div>

    <div class="card">

    <h2>Real-World Phishing Example: Warning Signs</h2>

    <p>
    Consider a hypothetical email claiming that an account
    will be suspended unless the recipient immediately
    verifies their password.
    </p>

    <div class="warning">
    Example warning signs:
    <ul>
    <li>Unexpected account-security notification.</li>
    <li>Pressure to act immediately.</li>
    <li>Link directing the recipient to an unfamiliar page.</li>
    <li>Request to provide login information.</li>
    </ul>
    </div>

    <p class="muted">
    This is an illustrative example, not a reproduced
    real-world phishing email.
    </p>

    </div>

    <div class="card">

    <h2>Cyber Ethics</h2>

    <ul>
    <li>Obtain informed and voluntary consent.</li>
    <li>Do not collect real passwords or OTPs.</li>
    <li>Do not impersonate real organisations in live campaigns.</li>
    <li>Do not publicly expose participant responses.</li>
    <li>Keep the demonstration restricted to its authorised environment.</li>
    <li>Explain the educational purpose of the exercise.</li>
    </ul>

    <a class="btn" href="/survey">
    Take Anonymous Awareness Survey
    </a>

    </div>
    """

    return layout("Phishing Awareness Guide", content)


# =====================================================
# 7. ANONYMOUS AWARENESS SURVEY
# =====================================================

def survey_page():

    content = """
    <div class="card">

    <h2>Anonymous Phishing Awareness Survey</h2>

    <p>
    This survey is designed to understand awareness
    of common phishing warning signs.
    </p>

    <div class="warning">

    <b>Participant Information and Consent</b>

    <p>
    Participation is voluntary. You may leave this page
    without submitting your answers.
    </p>

    <p>
    This educational survey does not request your name,
    email address, password, phone number or other
    identifying information.
    </p>

    <p>
    Responses are stored in the local project database
    and used only for aggregate academic analysis.
    </p>

    <p>
    Do not enter personal or confidential information.
    </p>

    <p>
    This survey is intended for adults aged 18 or older.
    Follow any additional consent or approval requirements
    set by your institution.
    </p>

    </div>

    <form id="surveyForm">

    <h3>
    1. Did you notice warning signs in the sample email?
    </h3>

    <label>
    <input type="radio" name="noticed" value="Yes" required>
    Yes
    </label><br>

    <label>
    <input type="radio" name="noticed" value="No">
    No
    </label><br>

    <label>
    <input type="radio" name="noticed" value="Not sure">
    Not sure
    </label>

    <hr>

    <h3>
    2. What would you do if you received a suspicious email?
    </h3>

    <label>
    <input type="radio" name="action" value="Report it" required>
    Report it
    </label><br>

    <label>
    <input type="radio" name="action" value="Verify the sender">
    Verify the sender
    </label><br>

    <label>
    <input type="radio" name="action" value="Click the link">
    Click the link
    </label><br>

    <label>
    <input type="radio" name="action" value="Ignore it">
    Ignore it
    </label>

    <hr>

    <h3>
    3. How confident are you in identifying phishing emails?
    </h3>

    <label>
    <input type="radio" name="confidence" value="Very confident" required>
    Very confident
    </label><br>

    <label>
    <input type="radio" name="confidence" value="Somewhat confident">
    Somewhat confident
    </label><br>

    <label>
    <input type="radio" name="confidence" value="Not confident">
    Not confident
    </label>

    <hr>

    <label>
    <input type="checkbox" id="consent" required>
    I am at least 18 years old, have read the information
    above and voluntarily agree to submit this anonymous survey.
    </label>

    <br><br>

    <button class="btn" type="submit">
    Submit Survey
    </button>

    </form>

    <p id="surveyMessage" class="muted"></p>

    </div>

    <script>

    document.getElementById("surveyForm").addEventListener(
      "submit", async function(e) {

        e.preventDefault();

        if (!document.getElementById("consent").checked) {
          return;
        }

        const data = {

          consent: true,

          noticed: document.querySelector(
            'input[name="noticed"]:checked').value,

          action: document.querySelector(
            'input[name="action"]:checked').value,

          confidence: document.querySelector(
            'input[name="confidence"]:checked').value
        };

        try {

          const response = await fetch("/survey-submit", {

            method: "POST",

            headers: {
              "Content-Type": "application/json"
            },

            body: JSON.stringify(data)

          });

          if (response.ok) {

            document.getElementById("surveyMessage").innerHTML =
              "<b>Thank you!</b> Your anonymous response was recorded.";

            this.reset();

          } else {

            document.getElementById("surveyMessage").textContent =
              "Unable to submit. Please try again.";

          }

        } catch (error) {

          document.getElementById("surveyMessage").textContent =
            "Connection error. Please try again.";

        }

      }
    );

    </script>
    """

    return layout("Anonymous Survey", content)


# =====================================================
# 8. SURVEY RESULTS AND ANALYSIS
# =====================================================

def survey_results_page():

    with sqlite3.connect(DB) as con:

        rows = con.execute("""
            SELECT noticed_red_flags, next_action, confidence
            FROM survey_responses
            WHERE consent = 1
        """).fetchall()

    total = len(rows)

    def make_rows(title, index):

        values = {}

        for row in rows:

            answer = row[index]

            values[answer] = values.get(answer, 0) + 1

        result = f"<h3>{title}</h3>"

        result += """
        <table>
        <tr>
        <th>Answer</th>
        <th>Responses</th>
        <th>Percentage</th>
        </tr>
        """

        if values:

            for answer, number in sorted(values.items()):

                percentage = (number / total) * 100

                result += (
                    f"<tr>"
                    f"<td>{escape(answer)}</td>"
                    f"<td>{number}</td>"
                    f"<td>{percentage:.1f}%</td>"
                    f"</tr>"
                )

        else:

            result += """
            <tr>
            <td colspan="3">No responses yet</td>
            </tr>
            """

        result += "</table>"

        return result

    content = f"""

    <div class="card">

    <h2>Anonymous Survey Results</h2>

    <div class="stat">
    <strong>{total}</strong>
    Total Submitted Responses
    </div>

    <p class="muted">
    Results are calculated from voluntarily submitted
    anonymous survey responses.
    </p>

    {make_rows("Recognition of Phishing Warning Signs", 0)}

    {make_rows("Intended Response to Suspicious Email", 1)}

    {make_rows("Confidence in Identifying Phishing", 2)}

    <hr>

    <p class="muted">
    No names or personal identities are displayed.
    Results should only be interpreted when actual
    voluntary responses have been received.
    </p>

    <a class="btn" href="/survey">Take Survey</a>

    <a class="btn" href="/awareness">Awareness Guide</a>

    </div>

    """

    return layout("Survey Results", content)


# =====================================================
# 9. REQUEST HANDLER
# =====================================================

class Handler(BaseHTTPRequestHandler):

    def send_html(self, content):

        data = content.encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.end_headers()

        self.wfile.write(data)


    def do_GET(self):

        path = urlparse(self.path).path

        if path == "/":

            self.send_html(dashboard())

        elif path == "/email":

            self.send_html(email_page())

        elif path == "/click":

            record("click")

            self.send_response(302)

            self.send_header("Location", "/landing")

            self.end_headers()

        elif path == "/landing":

            self.send_html(landing_page())

        elif path == "/stats":

            self.send_html(stats_page())

        elif path == "/report":

            record("reported")

            self.send_html(report_page())

        elif path == "/awareness":

            self.send_html(awareness_page())

        elif path == "/survey":

            self.send_html(survey_page())

        elif path == "/survey-results":

            self.send_html(survey_results_page())

        elif path == "/api/stats":

            data = json.dumps(counts()).encode()

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.end_headers()

            self.wfile.write(data)

        else:

            self.send_error(404)


    def do_POST(self):

        path = urlparse(self.path).path

        length = int(self.headers.get("Content-Length", 0))

        if length > 10000:

            self.send_error(413)

            return

        body = self.rfile.read(length) if length else b""

        if path == "/submit":

            # The demo form sends no field values.
            # Only the event is recorded.

            record("demo_submit")

            data = b'{"status":"recorded"}'


        elif path == "/survey-submit":

            try:

                answer = json.loads(body.decode("utf-8"))

                allowed = {

                    "noticed": [
                        "Yes",
                        "No",
                        "Not sure"
                    ],

                    "action": [
                        "Report it",
                        "Verify the sender",
                        "Click the link",
                        "Ignore it"
                    ],

                    "confidence": [
                        "Very confident",
                        "Somewhat confident",
                        "Not confident"
                    ]

                }

                if answer.get("consent") is not True:

                    self.send_error(400, "Consent required")

                    return

                noticed = answer.get("noticed")

                action = answer.get("action")

                confidence = answer.get("confidence")

                if (
                    noticed not in allowed["noticed"]
                    or action not in allowed["action"]
                    or confidence not in allowed["confidence"]
                ):

                    self.send_error(400, "Invalid survey response")

                    return

                with sqlite3.connect(DB) as con:

                    con.execute("""
                        INSERT INTO survey_responses
                        (
                            noticed_red_flags,
                            next_action,
                            confidence,
                            consent,
                            created
                        )
                        VALUES (?, ?, ?, ?, ?)
                    """, (

                        noticed,
                        action,
                        confidence,
                        1,
                        datetime.now().isoformat(timespec="seconds")

                    ))

                data = b'{"status":"survey_recorded"}'


            except (ValueError, UnicodeDecodeError):

                self.send_error(400, "Invalid request")

                return


        else:

            self.send_error(404)

            return


        self.send_response(200)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.end_headers()

        self.wfile.write(data)


    def log_message(self, fmt, *args):

        print("[LOCAL]", fmt % args)


# =====================================================
# 10. START APPLICATION
# =====================================================

if __name__ == "__main__":

    initialize()

    print("=" * 55)

    print(" CYBERSAFE - PHISHING AWARENESS SIMULATION")

    print("=" * 55)

    print(f"Dashboard: http://{HOST}:{PORT}")

    print("Press CTRL+C to stop the application.")

    print("=" * 55)

    HTTPServer((HOST, PORT), Handler).serve_forever()
