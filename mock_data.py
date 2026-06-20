import uuid

def get_mock_demo_data():
    """6-speaker Sprint Review mock data, offline fallback"""
    segments = [
        {"utt_index": 0, "start": 0.0, "speaker": "Speaker A", "text": "Good morning everyone, thanks for joining the sprint review. Let's go around and cover what was completed this sprint and what's planned next."},
        {"utt_index": 1, "start": 14.0, "speaker": "Speaker B", "text": "Sure. This sprint I finished the complete redesign of the user dashboard, including the new analytics widgets and the responsive layout for mobile devices. I also fixed five critical bugs in the authentication flow that were causing session timeouts. Currently I'm working on integrating the new design tokens across the component library, and today I'll start refactoring the navigation sidebar to match the updated style guide."},
        {"utt_index": 2, "start": 55.0, "speaker": "Speaker A", "text": "That's great progress, thank you. Carlos, what about the backend side?"},
        {"utt_index": 3, "start": 62.0, "speaker": "Speaker C", "text": "On the backend I completed the full migration of our database from the old schema to the new normalized structure, which took most of the sprint. I also optimized the slowest queries in the reporting module, cutting load time by sixty percent. Right now I'm building out the new caching layer using Redis, and I'm also currently testing the rate limiting middleware before we roll it out. Next sprint I plan to finalize the API versioning strategy so we can deprecate the old endpoints safely."},
        {"utt_index": 4, "start": 110.0, "speaker": "Speaker A", "text": "Excellent. David, how did QA go this sprint?"},
        {"utt_index": 5, "start": 117.0, "speaker": "Speaker D", "text": "This sprint I completed the full regression test suite for the checkout flow, covering all payment methods. I also wrote and finalized twelve new automated end-to-end tests for the user onboarding journey. I'm currently working through the accessibility audit for the dashboard, going screen by screen with a screen reader. Today I'll prepare the test report and share it with the team, and I should be able to wrap up the remaining accessibility fixes by tomorrow."},
        {"utt_index": 6, "start": 165.0, "speaker": "Speaker A", "text": "Sounds solid. Elena, you had the notifications work, right?"},
        {"utt_index": 7, "start": 172.0, "speaker": "Speaker E", "text": "Yes. I finished building the push notification service and integrated it with both iOS and Android clients. I also completed the email digest feature that summarizes weekly activity for each user. I'm still working on the in-app notification center UI, polishing the animations and making sure unread counts update correctly in real time. Today I plan to finalize the notification preferences screen so users can control which alerts they receive, and I'll also coordinate with Carlos on the backend events that trigger each notification type."},
        {"utt_index": 8, "start": 225.0, "speaker": "Speaker A", "text": "Great, thanks Elena. Frank, last but not least, how's the infrastructure work going?"},
        {"utt_index": 9, "start": 234.0, "speaker": "Speaker F", "text": "This sprint I completed the migration of our deployment pipeline to the new CI system, which already cut our build times in half. I also finalized the monitoring dashboards for production, with alerts wired up to the on-call rotation. Currently I'm working on setting up auto-scaling for the worker nodes, since we saw some load spikes last week. Today I'll start documenting the new infrastructure setup so the rest of the team can onboard easily, and I also need to coordinate with David on adding the new test environment to the pipeline."},
        {"utt_index": 10, "start": 290.0, "speaker": "Speaker A", "text": "This was a really strong sprint, everyone. Let's quickly talk about what's coming up. Looking at the backlog, our main priority is finishing the notification center, wrapping up the API versioning work, and getting the auto-scaling tested under real load."},
        {"utt_index": 11, "start": 312.0, "speaker": "Speaker B", "text": "From my side, after I finish the sidebar refactor today, I'll move on to reviewing the new component library documentation, and I should be able to start the settings page redesign by midweek."},
        {"utt_index": 12, "start": 330.0, "speaker": "Speaker C", "text": "I'll continue with the API versioning strategy as planned, and once that's finalized I'll start deprecating the old endpoints gradually, coordinating with the frontend team so nothing breaks."},
        {"utt_index": 13, "start": 348.0, "speaker": "Speaker D", "text": "I'll wrap up the accessibility fixes tomorrow as I mentioned, and then I'll start planning the test coverage for the new notification center once Elena's UI work is ready for testing."},
        {"utt_index": 14, "start": 365.0, "speaker": "Speaker E", "text": "Sounds good, I'll make sure to ping you David as soon as the notification center UI is stable enough to test."},
        {"utt_index": 15, "start": 375.0, "speaker": "Speaker F", "text": "And I'll prioritize getting the auto-scaling tested this week since that's blocking some of the load testing we wanted to do before the next release."},
        {"utt_index": 16, "start": 390.0, "speaker": "Speaker A", "text": "Perfect, thanks everyone for the updates. Let's reconvene same time next week. Have a great rest of your day, team."},
    ]

    tasks = [
        {"text": "Complete redesign of the user dashboard with analytics widgets", "status": "DONE", "keyword": "finished", "source_sentence": segments[1]["text"], "id": uuid.uuid4().hex},
        {"text": "Fix critical bugs in the authentication flow", "status": "DONE", "keyword": "fixed", "source_sentence": segments[1]["text"], "id": uuid.uuid4().hex},
        {"text": "Integrate new design tokens across component library", "status": "IN_PROGRESS", "keyword": "working", "source_sentence": segments[1]["text"], "id": uuid.uuid4().hex},
        {"text": "Refactor the navigation sidebar to match style guide", "status": "NEW_TASK", "keyword": "start", "source_sentence": segments[1]["text"], "id": uuid.uuid4().hex},

        {"text": "Migrate database to new normalized structure", "status": "DONE", "keyword": "completed", "source_sentence": segments[3]["text"], "id": uuid.uuid4().hex},
        {"text": "Optimize slow queries in the reporting module", "status": "DONE", "keyword": "optimized", "source_sentence": segments[3]["text"], "id": uuid.uuid4().hex},
        {"text": "Build new caching layer using Redis", "status": "IN_PROGRESS", "keyword": "building", "source_sentence": segments[3]["text"], "id": uuid.uuid4().hex},
        {"text": "Test rate limiting middleware", "status": "IN_PROGRESS", "keyword": "testing", "source_sentence": segments[3]["text"], "id": uuid.uuid4().hex},
        {"text": "Finalize API versioning strategy", "status": "NEW_TASK", "keyword": "finalize", "source_sentence": segments[3]["text"], "id": uuid.uuid4().hex},

        {"text": "Complete regression test suite for checkout flow", "status": "DONE", "keyword": "completed", "source_sentence": segments[5]["text"], "id": uuid.uuid4().hex},
        {"text": "Finalize automated end-to-end tests for onboarding", "status": "DONE", "keyword": "finalized", "source_sentence": segments[5]["text"], "id": uuid.uuid4().hex},
        {"text": "Work through accessibility audit for the dashboard", "status": "IN_PROGRESS", "keyword": "working", "source_sentence": segments[5]["text"], "id": uuid.uuid4().hex},
        {"text": "Prepare and share the test report", "status": "NEW_TASK", "keyword": "prepare", "source_sentence": segments[5]["text"], "id": uuid.uuid4().hex},

        {"text": "Build push notification service for iOS and Android", "status": "DONE", "keyword": "finished", "source_sentence": segments[7]["text"], "id": uuid.uuid4().hex},
        {"text": "Complete the email digest feature", "status": "DONE", "keyword": "completed", "source_sentence": segments[7]["text"], "id": uuid.uuid4().hex},
        {"text": "Work on the in-app notification center UI", "status": "IN_PROGRESS", "keyword": "working", "source_sentence": segments[7]["text"], "id": uuid.uuid4().hex},
        {"text": "Finalize the notification preferences screen", "status": "NEW_TASK", "keyword": "finalize", "source_sentence": segments[7]["text"], "id": uuid.uuid4().hex},

        {"text": "Migrate deployment pipeline to new CI system", "status": "DONE", "keyword": "completed", "source_sentence": segments[9]["text"], "id": uuid.uuid4().hex},
        {"text": "Finalize monitoring dashboards for production", "status": "DONE", "keyword": "finalized", "source_sentence": segments[9]["text"], "id": uuid.uuid4().hex},
        {"text": "Set up auto-scaling for worker nodes", "status": "IN_PROGRESS", "keyword": "working", "source_sentence": segments[9]["text"], "id": uuid.uuid4().hex},
        {"text": "Document the new infrastructure setup", "status": "NEW_TASK", "keyword": "start", "source_sentence": segments[9]["text"], "id": uuid.uuid4().hex},

        {"text": "Review new component library documentation", "status": "NEW_TASK", "keyword": "reviewing", "source_sentence": segments[11]["text"], "id": uuid.uuid4().hex},
        {"text": "Start settings page redesign", "status": "NEW_TASK", "keyword": "start", "source_sentence": segments[11]["text"], "id": uuid.uuid4().hex},
        {"text": "Deprecate old API endpoints gradually", "status": "NEW_TASK", "keyword": "deprecating", "source_sentence": segments[12]["text"], "id": uuid.uuid4().hex},
        {"text": "Plan test coverage for notification center", "status": "NEW_TASK", "keyword": "planning", "source_sentence": segments[13]["text"], "id": uuid.uuid4().hex},
        {"text": "Test auto-scaling under real load", "status": "NEW_TASK", "keyword": "prioritize", "source_sentence": segments[15]["text"], "id": uuid.uuid4().hex},
    ]
    return segments, tasks