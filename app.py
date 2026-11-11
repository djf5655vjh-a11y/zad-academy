import os, json, sqlite3, hashlib, secrets, datetime, re
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deploy-" + secrets.token_hex(8))
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
DB = os.environ.get("DATABASE_PATH", "zad_academy.db")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@zadacademy.local")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

SEED = [
 {"slug":"cyber-basics","title":"Cybersecurity Foundations","category":"Cybersecurity","icon":"🛡️","description":"Build safe security foundations, one mission at a time.","level":"Beginner","lessons":[
  ("The CIA Triad","Security has three core goals: confidentiality, integrity and availability. Confidentiality limits access, integrity protects accuracy, and availability keeps systems usable.",["Confidentiality, integrity, availability","Coding, internet, antivirus","CPU, input, access"],0,"What does confidentiality protect?","Keeping information accessible only to authorized people."),
  ("Passwords & MFA","Use unique long passwords and a password manager. Multi-factor authentication adds another proof of identity beyond a password.",["Reuse one strong password","Use unique passwords and MFA","Share passwords with teammates"],1,"What does MFA add?","An additional verification factor."),
  ("Responsible Testing","Only test systems when you own them or have clear written permission. Practice in intentionally vulnerable labs and isolated environments.",["Any public website","Only systems with permission","A friend's account"],1,"Where should beginners practice?","In authorized training labs.")
 ]},
 {"slug":"networking","title":"Networking Basics","category":"Cybersecurity","icon":"🌐","description":"Understand how devices communicate.","level":"Beginner","lessons":[
  ("IP Addresses","An IP address identifies a device interface on a network. Private address ranges are commonly used inside homes and organizations.",["A network identifier","A programming language","A password"],0,"What does an IP address identify?","A device interface on a network."),
  ("DNS","DNS translates human-readable domain names into IP addresses so clients can find services.",["Encrypts files","Resolves domain names","Creates passwords"],1,"What is DNS mainly used for?","Resolving domain names to IP addresses.")
 ]},
 {"slug":"python","title":"Python Quest","category":"Programming","icon":"🐍","description":"Learn Python through bite-sized coding missions.","level":"Beginner","lessons":[
  ("Variables","Variables are names that refer to values. Example: score = 10 stores an integer value under the name score.",["score = 10","10 = score","var score := 10"],0,"Which is valid Python assignment?","score = 10"),
  ("Conditions","An if statement runs a block when its condition is true. Indentation defines the block in Python.",["if score > 5:","when score > 5","if (score > 5) then"],0,"Which keyword starts a condition?","if"),
  ("Loops","A for loop iterates over items in a sequence or other iterable.",["for","repeat_until","iterate:"],0,"Which loop is commonly used to iterate over a list?","for")
 ]},
 {"slug":"html-css","title":"Web Builder","category":"Programming","icon":"🧩","description":"Create the structure and style of websites.","level":"Beginner","lessons":[
  ("HTML Structure","HTML describes the structure and meaning of web content using elements such as headings, paragraphs and links.",["HTML structures content","HTML stores passwords","HTML replaces databases"],0,"What is HTML primarily for?","Structuring web content."),
  ("CSS Styling","CSS controls presentation such as colors, spacing, layout and responsive behavior.",["Styling web pages","Managing server secrets","Querying SQL tables"],0,"Which technology styles a web page?","CSS")
 ]},
 {"slug":"java","title":"Java Starter","category":"Programming","icon":"☕","description":"Learn Java syntax and object-oriented basics.","level":"Beginner","lessons":[
  ("Java Basics","Java is a statically typed programming language. A class is a common building block of Java programs.",["A class","A CSS selector","A DNS record"],0,"Which keyword declares a class?","class"),
  ("Types","Java variables have declared types such as int, boolean and String.",["int","style","href"],0,"Which is an integer type in Java?","int")
 ]},
 {"slug":"web-safety","title":"Web Security Lab","category":"Cybersecurity","icon":"🔐","description":"Learn defensive web security using safe examples.","level":"Intermediate","lessons":[
  ("Input Validation","Validate input on the server, use parameterized queries, and apply output encoding appropriate to the context.",["Trust all user input","Validate and encode input","Disable server logs"],1,"What is a safer database query approach?","Parameterized queries."),
  ("OWASP Awareness","The OWASP Top 10 is an awareness document about important web application security risks.",["A browser","A web security awareness list","A programming language"],1,"What does OWASP Top 10 describe?","Important web application security risks.")
 ]},
 {"slug":"sql","title":"SQL Explorer","category":"Programming","icon":"🗃️","description":"Explore databases and structured queries.","level":"Beginner","lessons":[
  ("SELECT","SELECT retrieves data from one or more database tables.",["SELECT","PAINT","ROUTE"],0,"Which SQL keyword retrieves rows?","SELECT"),
  ("Filtering","WHERE filters rows based on a condition.",["WHERE","COLOR","STYLE"],0,"Which clause filters rows?","WHERE")
 ]},
 {"slug":"linux","title":"Linux Terminal","category":"Technology","icon":"🐧","description":"Understand files, permissions and shell basics.","level":"Beginner","lessons":[
  ("Files & Folders","Linux organizes files in a directory tree. Learn commands in a local practice environment.",["Directories organize files","Directories are passwords","Directories are IP addresses"],0,"What do directories organize?","Files and folders."),
  ("Permissions","File permissions determine who can read, write or execute a file.",["Read, write, execute","Upload, like, share","Encrypt, route, ping"],0,"Name the common permission types.","Read, write and execute.")
 ]},
 {"slug":"ai","title":"AI & Machine Learning","category":"Technology","icon":"🤖","description":"Start with data, models and responsible AI.","level":"Beginner","lessons":[
  ("What is a Model?","A machine-learning model learns patterns from data and uses them to make predictions or generate outputs.",["A learned pattern system","A monitor cable","A file extension"],0,"What does a model learn from?","Data."),
  ("Responsible AI","Check outputs for accuracy, bias and privacy risks. Human review matters in important decisions.",["Trust every output","Review accuracy, bias and privacy","Share private data"],1,"What should you review?","Accuracy, bias and privacy.")
 ]}
]

def init_db():
    c=db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT DEFAULT 'student', xp INTEGER DEFAULT 0, streak INTEGER DEFAULT 0, last_active TEXT, premium_until TEXT, created_at TEXT);
    CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY, slug TEXT UNIQUE, title TEXT, category TEXT, icon TEXT, description TEXT, level TEXT, published INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS lessons(id INTEGER PRIMARY KEY, course_id INTEGER, title TEXT, body TEXT, options TEXT, answer INTEGER, question TEXT, explanation TEXT, position INTEGER);
    CREATE TABLE IF NOT EXISTS progress(id INTEGER PRIMARY KEY, user_id INTEGER, lesson_id INTEGER, completed_at TEXT, UNIQUE(user_id,lesson_id));
    CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY, user_id INTEGER, plan TEXT, amount TEXT, utr TEXT, status TEXT DEFAULT 'pending', created_at TEXT);
    """)
    if c.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
        for course in SEED:
            cur=c.execute("INSERT INTO courses(slug,title,category,icon,description,level) VALUES(?,?,?,?,?,?)",
                (course["slug"],course["title"],course["category"],course["icon"],course["description"],course["level"]))
            cid=cur.lastrowid
            for i,(title,body,opts,ans,q,ex) in enumerate(course["lessons"]):
                c.execute("INSERT INTO lessons(course_id,title,body,options,answer,question,explanation,position) VALUES(?,?,?,?,?,?,?,?)",
                    (cid,title,body,json.dumps(opts),ans,q,ex,i))
    if not c.execute("SELECT id FROM users WHERE email=?",(ADMIN_EMAIL,)).fetchone():
        c.execute("INSERT INTO users(name,email,password,role,created_at) VALUES(?,?,?,?,?)",
                  ("ZAD Admin",ADMIN_EMAIL,generate_password_hash(ADMIN_PASSWORD),"admin",datetime.date.today().isoformat()))
    c.commit(); c.close()

init_db()

def current_user():
    if "uid" not in session: return None
    c=db(); u=c.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone(); c.close()
    return u

def login_required(fn):
    @wraps(fn)
    def wrap(*a,**kw):
        if not current_user(): return redirect(url_for("login",next=request.path))
        return fn(*a,**kw)
    return wrap

def admin_required(fn):
    @wraps(fn)
    def wrap(*a,**kw):
        u=current_user()
        if not u or u["role"]!="admin": abort(403)
        return fn(*a,**kw)
    return wrap

@app.context_processor
def inject():
    return {"user":current_user(),"year":datetime.date.today().year}

@app.route("/")
def index():
    if current_user(): return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form.get("name","").strip()[:60]
        email=request.form.get("email","").strip().lower()
        pw=request.form.get("password","")
        if not name or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",email) or len(pw)<8:
            flash("Enter a valid name/email and password with at least 8 characters.","error")
        else:
            c=db()
            try:
                cur=c.execute("INSERT INTO users(name,email,password,created_at) VALUES(?,?,?,?)",
                    (name,email,generate_password_hash(pw),datetime.date.today().isoformat()))
                c.commit(); session["uid"]=cur.lastrowid
                return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError: flash("That email is already registered.","error")
            finally: c.close()
    return render_template("auth.html",mode="register")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email","").strip().lower(); pw=request.form.get("password","")
        c=db(); u=c.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone(); c.close()
        if u and check_password_hash(u["password"],pw):
            session["uid"]=u["id"]; return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Email or password is incorrect.","error")
    return render_template("auth.html",mode="login")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    u=current_user(); c=db()
    courses=c.execute("SELECT co.*,COUNT(l.id) lesson_count FROM courses co LEFT JOIN lessons l ON l.course_id=co.id WHERE co.published=1 GROUP BY co.id ORDER BY co.id").fetchall()
    done=c.execute("SELECT COUNT(*) FROM progress WHERE user_id=?",(u["id"],)).fetchone()[0]
    total=c.execute("SELECT COUNT(*) FROM lessons l JOIN courses co ON co.id=l.course_id WHERE co.published=1").fetchone()[0]
    leaders=c.execute("SELECT name,xp FROM users WHERE role='student' ORDER BY xp DESC LIMIT 5").fetchall()
    c.close()
    return render_template("dashboard.html",courses=courses,done=done,total=total,leaders=leaders)

@app.route("/course/<slug>")
@login_required
def course(slug):
    c=db(); co=c.execute("SELECT * FROM courses WHERE slug=? AND published=1",(slug,)).fetchone()
    if not co: c.close(); abort(404)
    lessons=c.execute("SELECT l.*,CASE WHEN p.id IS NULL THEN 0 ELSE 1 END completed FROM lessons l LEFT JOIN progress p ON p.lesson_id=l.id AND p.user_id=? WHERE l.course_id=? ORDER BY l.position",(session["uid"],co["id"])).fetchall()
    c.close(); return render_template("course.html",course=co,lessons=lessons)

@app.route("/lesson/<int:lesson_id>",methods=["GET","POST"])
@login_required
def lesson(lesson_id):
    c=db()
    l=c.execute("SELECT l.*,co.title course_title,co.slug FROM lessons l JOIN courses co ON co.id=l.course_id WHERE l.id=? AND co.published=1",(lesson_id,)).fetchone()
    if not l: c.close(); abort(404)
    if request.method=="POST":
        try: choice=int(request.form.get("choice","-1"))
        except ValueError: choice=-1
        if choice==l["answer"]:
            today=datetime.date.today().isoformat()
            c.execute("INSERT OR IGNORE INTO progress(user_id,lesson_id,completed_at) VALUES(?,?,?)",(session["uid"],lesson_id,today))
            if c.execute("SELECT changes()").fetchone()[0]:
                u=c.execute("SELECT xp,last_active,streak FROM users WHERE id=?",(session["uid"],)).fetchone()
                streak=u["streak"] if u["last_active"]==today else (u["streak"]+1 if u["last_active"]==(datetime.date.today()-datetime.timedelta(days=1)).isoformat() else 1)
                c.execute("UPDATE users SET xp=xp+20,streak=?,last_active=? WHERE id=?",(streak,today,session["uid"]))
            c.commit(); c.close()
            return render_template("answer.html",correct=True,explanation=l["explanation"],next_url=url_for("course",slug=l["slug"]))
        c.close(); return render_template("answer.html",correct=False,explanation="Not quite. Review the lesson and try again.",next_url=url_for("lesson",lesson_id=lesson_id))
    options=json.loads(l["options"]); c.close()
    return render_template("lesson.html",lesson=l,options=options)

@app.route("/leaderboard")
@login_required
def leaderboard():
    c=db(); rows=c.execute("SELECT name,xp,streak FROM users WHERE role='student' ORDER BY xp DESC LIMIT 50").fetchall(); c.close()
    return render_template("leaderboard.html",rows=rows)

@app.route("/profile")
@login_required
def profile():
    u=current_user(); c=db()
    done=c.execute("SELECT COUNT(*) FROM progress WHERE user_id=?",(u["id"],)).fetchone()[0]
    c.close(); return render_template("profile.html",done=done)

@app.route("/premium",methods=["GET","POST"])
@login_required
def premium():
    if request.method=="POST":
        plan=request.form.get("plan","monthly")
        amount="199" if plan=="monthly" else "1499"
        utr=request.form.get("utr","").strip()
        if len(utr)<6 or len(utr)>40:
            flash("Enter your valid payment reference / UTR.","error")
        else:
            c=db(); c.execute("INSERT INTO payments(user_id,plan,amount,utr,created_at) VALUES(?,?,?,?,?)",
                (session["uid"],plan,amount,utr,datetime.datetime.now().isoformat(timespec="seconds"))); c.commit(); c.close()
            flash("Request submitted. Premium activates after admin verification.","success")
            return redirect(url_for("premium"))
    c=db(); history=c.execute("SELECT * FROM payments WHERE user_id=? ORDER BY id DESC",(session["uid"],)).fetchall(); c.close()
    return render_template("premium.html",history=history)

@app.route("/admin")
@admin_required
def admin():
    c=db()
    users=c.execute("SELECT id,name,email,role,xp,streak,premium_until FROM users ORDER BY id DESC LIMIT 100").fetchall()
    payments=c.execute("SELECT p.*,u.name,u.email FROM payments p JOIN users u ON u.id=p.user_id ORDER BY p.id DESC").fetchall()
    courses=c.execute("SELECT co.*,COUNT(l.id) lesson_count FROM courses co LEFT JOIN lessons l ON l.course_id=co.id GROUP BY co.id ORDER BY co.id").fetchall()
    c.close(); return render_template("admin.html",users=users,payments=payments,courses=courses)

@app.route("/admin/payment/<int:pid>/<action>",methods=["POST"])
@admin_required
def payment_action(pid,action):
    if action not in ("approve","reject"): abort(400)
    c=db(); p=c.execute("SELECT * FROM payments WHERE id=?",(pid,)).fetchone()
    if p:
        c.execute("UPDATE payments SET status=? WHERE id=?",("approved" if action=="approve" else "rejected",pid))
        if action=="approve":
            days=30 if p["plan"]=="monthly" else 365
            expiry=(datetime.date.today()+datetime.timedelta(days=days)).isoformat()
            c.execute("UPDATE users SET premium_until=? WHERE id=?",(expiry,p["user_id"]))
    c.commit(); c.close(); flash("Payment request updated.","success"); return redirect(url_for("admin"))

@app.route("/admin/course",methods=["POST"])
@admin_required
def add_course():
    title=request.form.get("title","").strip()[:100]; category=request.form.get("category","Technology")[:40]
    slug=re.sub(r"[^a-z0-9]+","-",title.lower()).strip("-")
    if title and slug:
        c=db()
        try: c.execute("INSERT INTO courses(slug,title,category,icon,description,level) VALUES(?,?,?,?,?,?)",
            (slug,title,category,request.form.get("icon","📘")[:8],request.form.get("description","")[:250],request.form.get("level","Beginner")))
        except sqlite3.IntegrityError: flash("Course already exists.","error")
        c.commit(); c.close()
    return redirect(url_for("admin"))

@app.route("/admin/lesson",methods=["POST"])
@admin_required
def add_lesson():
    c=db(); co=c.execute("SELECT id FROM courses WHERE id=?",(request.form.get("course_id"),)).fetchone()
    if co:
        opts=[x.strip() for x in request.form.get("options","").split("|") if x.strip()]
        try: answer=int(request.form.get("answer","0"))
        except ValueError: answer=0
        if len(opts)>=2 and 0<=answer<len(opts):
            pos=c.execute("SELECT COALESCE(MAX(position),-1)+1 FROM lessons WHERE course_id=?",(co["id"],)).fetchone()[0]
            c.execute("INSERT INTO lessons(course_id,title,body,options,answer,question,explanation,position) VALUES(?,?,?,?,?,?,?,?)",
                (co["id"],request.form.get("title","New lesson")[:100],request.form.get("body","")[:3000],json.dumps(opts),answer,request.form.get("question","")[:500],request.form.get("explanation","")[:1000],pos))
            c.commit()
    c.close(); return redirect(url_for("admin"))

@app.route("/admin/user/<int:uid>/xp",methods=["POST"])
@admin_required
def adjust_xp(uid):
    try: amount=max(-100000,min(100000,int(request.form.get("amount","0"))))
    except ValueError: amount=0
    c=db(); c.execute("UPDATE users SET xp=MAX(0,xp+?) WHERE id=?",(amount,uid)); c.commit(); c.close()
    return redirect(url_for("admin"))

@app.route("/health")
def health(): return jsonify(status="ok",app="ZAD ACADEMY")

@app.errorhandler(403)
def forbidden(e): return render_template("error.html",code=403,message="Admin access required."),403
@app.errorhandler(404)
def missing(e): return render_template("error.html",code=404,message="This learning path was not found."),404

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
