# Bakaláři CLI

An unofficial CLI tool for the Czech school information system Bakaláři.

## Installation

Sorry, this project is still in development.

## Commands

### Auth

```bash
# Login using the interface
baka login

# Output
> Enter your city: [city]
> Enter your school: [school]
> Enter your username: [username]
> Enter your password: [password]
```

```bash
# Login directly using arguments
baka login [school_url] [username] [password]
```

Access and refresh tokens are stored in the operating system keyring. The `auth.json` file contains only the school URL. Existing `auth.json` files with tokens are migrated to the keyring the next time the configuration is loaded.

### Grades

```bash
# Display all grades
baka grades

# Output
GPA: 2.63 / 4

... # Grades
```

```bash
# Display grades only from the specified subjects
baka grades M CHE ELE [...subjects]

# Output
----- Mathematics -----

Average: 1.75

2-  |   27.11.2026   |   Applications of differential calculus
1   |   12.7.2026    |   Inverse matrix, determinant

----- Chemistry -----

Average: 4.5

4-  |   19.10.2026   |   Introduction to organic chemistry

----- Electrical engineering -----

Average: 0.97

100 |   20.12.2026   |   Series vs parallel circuits
94  |   7.1.2027     |   Ohm's law
```

```bash
# Display final grades
baka grades --final M CHE ELE [...subjects]

# Output
----- Year 1 -----

1. Semester

2. Semester

...
```

### Subjects

```bash
# Display all subjects
baka subjects

# Output
M     |   Mathematics              | Bc. Adin Peterson
HAR   |   Hardware                 | Ing. Bc. Patrick Stephenson
ELE   |   Electrical engineering   | Ing. John Smith, Ph.D.
...
```

### Substitutions (not-yet implemented)

### Komens (not-yet implemented)

```bash
# Display recieved messages
baka komens recieved
baka komens recieved --read
baka komens recieved --unread

# Output
```

```bash
# Display sent messages
baka komens sent

# Output
```

```bash
baka komens new

# Output
> Enter the recipient type: [Teacher]
> Enter the recipients: [recipient1] [recipient2] [...recipients]
> Enter the title: [New message]
> Enter the body:
Dear teacher,
blah blah blah
```