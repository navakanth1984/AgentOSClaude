# Session Memory (Bucket 1)

This directory acts as an append-only archive. 

**Protocol:** 
At the end of a work session, execute a "wrap-up" command to summarize the conversation history, insights gained, and tasks completed. Save that summary as a timestamped markdown file in this directory.

This allows the AI to recall exact steps taken across multiple disjointed sessions without polluting the real-time working context.
