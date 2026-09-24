<p align="center">
  <a href="https://search2o.com">
    <img src="https://search2o.com/images/og.png" alt="Search2o: a platform to build, run, and use AI agents, with a search interface" width="600">
  </a>
</p>

**Website:** [search2o.com](https://search2o.com) · **Docs:** [Using Search2o from an assistant](https://search2o.com/docs/skill-integration/index.html)

# Search2o skill

An [Agent Skill](https://agentskills.io) that lets an AI assistant find and run your
company's Search2o agents. The assistant searches for the agent that fits what the person
asked, runs it, asks the person any questions the agent needs answered, and shows the
result.

The same folder works in every client that implements the Agent Skills standard, among them
Claude Code, Cursor and OpenAI Codex.

## What you need

- A Search2o account with published agents, and an agent server the person's machine can reach.
- An integration token for each person who uses the skill. Create one from your profile in
  the Search2o GUI. A token acts as that person: it can search, run agents and manage that
  person's own conversations, and it can never read or change configuration, manage users
  or read reports, whatever the person's role.

## Install

Copy the `search2o` folder into the client's skills directory. For Claude Code:

```bash
cp -R search2o ~/.claude/skills/
```

Then give the script the server address and the token, either as environment variables:

```bash
export SEARCH2O_SERVER=https://search2o.example.com
export SEARCH2O_TOKEN=<the integration token>
```

or as files, which is what to use when the client does not keep environment variables
between sessions:

```bash
mkdir -p ~/.search2o
echo -n https://search2o.example.com > ~/.search2o/server
echo -n <the integration token> > ~/.search2o/token
chmod 600 ~/.search2o/token
```

The token is never stored in the skill's files. Revoke it from the GUI when it is no longer
needed, and revoke any token that has been pasted into a chat.

## What is in the folder

```
search2o/
  SKILL.md          the instructions, and the description that triggers the skill
  reference.md      request and response shapes, result codes, output types
  scripts/s2o.py    the two calls, search and execAgent
```

`SKILL.md`'s description decides when the assistant reaches for the skill. Edit its examples
to name the kinds of work your agents actually do, so it triggers on your company's requests
and stays out of the way otherwise.

## Trying it

```bash
python3 search2o/scripts/s2o.py search '{"query": "where is order 4182"}'
python3 search2o/scripts/s2o.py execAgent '{"agentName": "order_status", "inputs": {"query": "where is order 4182"}}'
```

Each call prints one JSON object. A failed call prints a message and exits non-zero.
