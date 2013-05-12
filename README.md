gamma
===========

gamma is a programming contest management system and environment,
designed for use in an annual programming contest for Icelandic
high school students.


Design and goals
----------------

- Use Python 2.7 throughout

The project is split into two main parts:

- Web interface

    - Use Tornado as a web server/framework
    - Use SqlAlchemy as a db handler/ORM mapper
    - Use PostgreSql as a database
    - Use Twitter Bootstrap
    - Use jQuery
    - Internalization from start (mainly English and Icelandic)
    - User/team management
    - Programming contest interface
    - Manage contests
        - Choose available programming languages
        - Create problems, as well as test cases and solutions
    - Live scoreboard
    - Place to post solutions, and vote on them (and perhaps comment), behind each problem (similar to Project Euler)
    - Each user can form a team, and then apply for a contest. This only applies to contests where teams are allowed.

- Judge backend

    - Application for human judges to judge solutions
    - Keep open the possibility of adding an automatic judge
