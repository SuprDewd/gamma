# coding: utf8
from models import *
import datetime
import random

def add_test_data(app, db):

    cpp = ProgrammingLanguage(name='C++', compile_cmd="g++ %(file)s -o %(exe)s -O3", run_cmd="./%(exe)s")
    db.add(cpp)
    db.flush()

    fk2012 = Contest(name=u'Forritunarkeppni Framhaldsskólanna 2012',
                     public=True,
                     start_time=datetime.datetime(2012, 3, 16, 9, 0, 0),
                     registration_start=datetime.datetime(2012, 1, 1, 0, 0, 0))

    db.add(fk2012)
    db.flush()

    p1 = Problem(name=u'Lóðarí',
                 public=True,
                 description=u"""
		<p>Sveitarfélag nokkurt á austurlandi hefur nýlega hafið að selja ferningslaga lóðir. Lóðirnar liggja allar í beinni línu frá norðri til suðurs, en vegna skipulagsmistaka, þá er engin lóð jafn stór og önnur, því fyrir sérhverja lóð, þá er lóðin fyrir sunnan hana einum metra lengri á hvorn kant. Þetta hefur valdið bæjaryfirvöldum miklum höfuðverk og þið hafið verið kölluð til aðstoðar.</p>

		<p>Þið fáið það hlutverk að skrifa forrit sem að reiknar muninn á flatarmáli samliggjandi lóða. Það er, að gefinni hliðarlengd lóðar (sem er ekki syðsta lóðin), þá eigið þið að reikna út hversu mörgum fermetrum stærri lóðin er fyrir sunnan gefnu lóðina.</p>

		<h2>Inntak</h2>
		<p>Inntakið byrjar á einni heiltölu <tt>C</tt>, sem gefur fjölda prófunartilvika sem á eftir koma. Hvert prófunartilvik samanstendur af einni línu sem inniheldur eina heiltölu <tt>1 &leq; x &leq; 100000</tt>, sem gefur hliðarlengd lóðar.</p>

		<h2>Úttak</h2>
		<p>Fyrir sérhvert prófunartilvik á að skrifa út eina línu sem inniheldur eina heiltölu, sem gefur hversu mörgum fermetrum lóðin fyrir sunnan gefnu lóðina er stærri en gefna lóðin.</p>

		<h2>Dæmi um inntak</h2>
<pre><tt>2
3
8</tt></pre>
	
		<h2>Dæmi um úttak</h2>
<pre><tt>7
17</tt></pre>
                 """,
                 solution=u"""
#include<iostream>

using namespace std;

#ifndef ONLINE_JUDGE
#define DEBUG 0
#endif
//-------------------
#ifdef ONLINE_JUDGE
#define DEBUG 0
#endif
#if DEBUG > 1
#define dout cout
#else
#define dout 0 && cout
#endif
#if DEBUG > 0
#include<cstdio>
#define read(file) freopen(file,"r",stdin)
#define write(file) freopen(file,"w",stdout)
#else
#define read(file)
#define write(file)
#endif

int main()
{
    read("in.txt");

    int test_cases;
    int curr;
    cin >> test_cases;

    while(test_cases--)
    {
        cin >> curr;
        cout << 2 * curr + 1 << '\n';
    }
    return 0;
}
                 """,
                 solution_lang_id=cpp.id,
                 time_limit=3*1000,
                 memory_limit=64*1024*1024)

    db.add(p1)
    db.flush()

    p1c = ContestProblem(short_id='A', problem_id=p1.id, contest_id=fk2012.id)
    db.add(p1c)
    db.flush()

    p1t1 = Test(problem_id=p1.id,
            input=u"""5
1
2
3
7
15
""", output=u"""3
5
7
15
31
""")
    db.add(p1t1)
    db.flush()

    p2 = Problem(name="Biskupinn", public=True, description=u"""
		<p>Í þessu verkefni ímyndum við okkur að við séum með <tt>N&times;N</tt> skákborð og
jafnframt ímyndum við okkur að það sé aðeins einn leikmaður á borðinu, þ.e.
biskupinn. Staðsetningar, eða reitir, á skákborðinu eru táknaðar með raðpari <tt>(r,c)</tt>, þ.a. <tt>1 &leq; r,c &leq; N</tt>, þar sem <tt>r</tt> segir til um í hvaða röð reiturinn er og <tt>c</tt> segir til um í hvaða dálki reiturinn er. Staðsetningin <tt>(1,1)</tt> vísar þá til reitsins
sem er neðst í vinstra horninu og <tt>(N,N)</tt> vísar til reitsins efst í hægra horninu.</p>

		<p>Verkefni ykkar er nú að finna fæstu mögulegu hreyfingar sem þarf til að koma biskupnum á ákveðinn
reit á skákborðinu, ef það er yfir höfuð hægt. Hreyfingar biskupsins eru eins og í hefðbundinni skák,
þ.e. hann getur ferðast á ská eins marga reiti og vera vill.</p>

		<h2>Inntak</h2>
		<p>Inntakið byrjar á einni heiltölu <tt>C</tt>, sem gefur fjölda prófunartilvika sem á eftir koma. Á eftir þessari línu
kemur auð lína, og að auki kemur auð lína milli prófunartilvika.</p>

		<p>Fyrsta lína hvers prófunartilviks inniheldur eina heiltölu <tt>1 &leq; T &leq; 100</tt>, sem gefur fjölda prófana í því
prófunartilviki. Önnur línan inniheldur eina heiltölu <tt>1 &leq; N &leq; 100.000.000</tt> (stærð skákborðsins er <tt>N&times;N</tt>). Á eftir þeirri línu koma svo <tt>T</tt> línur, hver með einni prófun. Hver lína inniheldur fjórar
heiltölur, aðskildar með einu orðabili. Fyrstu tvær tölurnar gefa röð og dálk biskupsins og seinni tvær
gefa röð og dálk reitsins sem að biskupinn vill komast á.</p>

		<h2>Úttak</h2>
		<p>Fyrir sérhverja prófun, á að skrifa út eina línu. Línan á að innihalda eina heiltölu, sem gefur minnsta
fjölda hreifinga sem þarf til að færa biskupinn á gefna reitinn, eða <tt>&ldquo;impossible&rdquo;</tt> ef ómögulegt er
fyrir biskupinn að komast á reitinn.</p>

		<h2>Dæmi um inntak</h2>
<pre><tt>2

3
8
3 6 6 3
4 2 2 3
7 2 1 4

2
6
1 2 6 5
2 3 5 1</tt></pre>
	
		<h2>Dæmi um úttak</h2>
<pre><tt>1 
impossible 
2 
2 
impossible</tt></pre>
            """, solution=u"""
#include<iostream>

using namespace std;

#ifndef ONLINE_JUDGE
#define DEBUG 0
#endif
//-------------------
#ifdef ONLINE_JUDGE
#define DEBUG 0
#endif
#if DEBUG > 1
#define dout cout
#else
#define dout 0 && cout
#endif
#if DEBUG > 0
#include<cstdio>
#define read(file) freopen(file,"r",stdin)
#define write(file) freopen(file,"w",stdout)
#else
#define read(file)
#define write(file)
#endif

int total_test_cases, test_cases, board_size;
int bishop_r, bishop_c;
int target_r, target_c;

int abs(int a)
{
    return a < 0 ? -a : a;
}

int main()
{
    read("in.txt");

    cin >> total_test_cases;

    while(total_test_cases--)
    {
        cin >> test_cases;
        cin >> board_size;
        while(test_cases--)
        {
            cin >> bishop_r >> bishop_c >> target_r >> target_c;
            if( (bishop_r + bishop_c) % 2 != (target_r + target_c) % 2 )
            {
                cout << "impossible\n";
            }
            else if(bishop_r == target_r && bishop_c == target_c)
            {
                cout << 0 << '\n';
            }
            else if( abs(bishop_r - target_r) == abs(bishop_c - target_c) )
            {
                cout << 1 << '\n';
            }
            else
            {
                cout << 2 << '\n';
            }
        }
    }
    return 0;
}
            """, solution_lang_id=cpp.id, time_limit=3*1000, memory_limit=64*1024*1024)

    db.add(p2)
    db.flush()

    p2c = ContestProblem(short_id='B', problem_id=p2.id, contest_id=fk2012.id)
    db.add(p2c)
    db.flush()

    p2t1 = Test(problem_id=p2.id, input=u"""3

4
8
3 6 6 3
4 2 2 3
7 2 1 4
3 3 3 3

9
12
1 1 10 10
1 1 10 9
1 2 7 4
6 3 4 1
6 3 2 7
6 3 7 2
6 3 11 8
6 5 4 5
6 5 6 6

2
10000000
150 723 9010024 7234123
1 1 10000000 10000000
""", output=u"""1
impossible
2
0
1
impossible
2
1
1
1
1
2
impossible
2
1
""")
    db.add(p2t1)
    db.flush()

    test_user = User(username="test", password_hash=util.hash_password("test", "test", app.settings["cookie_secret"]), email='test@test.com', active=True)
    db.add(test_user)
    db.flush()
    test_user_team = Team(name="test", locked=True)
    db.add(test_user_team)
    db.flush()
    db.add(TeamMember(user_id=test_user.id, team_id=test_user_team.id, leader=True))
    db.flush()

    db.add(Registration(team_id=test_user_team.id, contest_id=fk2012.id))

    cs_p1_1 = ContestSubmission(team_id=test_user_team.id, problem_id=p1.id, contest_id=fk2012.id, submitted=101, verdict='WA', solution='', solution_lang_id=cpp.id)
    cs_p1_2 = ContestSubmission(team_id=test_user_team.id, problem_id=p1.id, contest_id=fk2012.id, submitted=111, verdict='AC', solution='', solution_lang_id=cpp.id)
    cs_p2_1 = ContestSubmission(team_id=test_user_team.id, problem_id=p2.id, contest_id=fk2012.id, submitted=39, verdict='WA', solution='', solution_lang_id=cpp.id)

    db.add(cs_p1_1)
    db.add(cs_p1_2)
    db.add(cs_p2_1)

    for i in range(-100, 8):
        db.add(Contest(name='Test %d' % i,
            public=True,
            start_time=datetime.datetime.now() + datetime.timedelta(0, i * 60 * 60, 0),
            registration_start=datetime.datetime.now() + datetime.timedelta(0, i * 60 * 60, 0) - datetime.timedelta(0, 2 * 60 * 60, 0),
            registration_end=datetime.datetime.now() + datetime.timedelta(0, i * 60 * 60, 0) - datetime.timedelta(0, 1 * 60 * 60, 0),
            duration=3 * 60))

    db.add(Message(user_to_id=test_user.id, user_from_id=test_user.id, subject=u"Halló Heimur", content=u"Halló! Þetta er prufa..."))
    db.add(Message(user_to_id=test_user.id, user_from_id=test_user.id, subject=u"Meeoooww", content=u"Halló! Þetta er meiri prufa..."))
    db.add(Message(user_to_id=test_user.id, user_from_id=test_user.id, subject=u"Mooo", content=u"Þetta er meiri prufa...", read=True))

    db.commit()

