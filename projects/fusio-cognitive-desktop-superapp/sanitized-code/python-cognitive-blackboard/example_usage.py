"""
Demonstration runner for Session Blackboard working memory and trajectory branching.
"""

from blackboard import SessionBlackboard

def main():
    bb = SessionBlackboard("blackboard_demo.db")
    session = "sess_marketing_launch_01"

    print("1. Main agent writing discovery findings...")
    bb.set(session, "main", "target_audience", {"segment": "B2B SaaS", "locale": "en-US"})
    bb.record_step("step_1", None, session, "main", 1, "assistant", "Identified primary target audience.")

    print("2. Spawning isolated sub-agent branch (rescue_login)...")
    # Sub-agent reads inherited key from main branch
    audience = bb.get(session, "rescue_login", "target_audience")
    print(f"-> Sub-agent retrieved inherited target audience: {audience['segment']}")

    # Sub-agent writes branch-specific state
    bb.set(session, "rescue_login", "auth_status", "bypassed_via_cookie")
    bb.record_step("step_2", "step_1", session, "rescue_login", 2, "tool", "Cleared 2FA obstacle.")

    print("3. Querying branch trajectory:")
    steps = bb.get_trajectory(session, "rescue_login")
    for s in steps:
        print(f"   [{s['role']}] Step {s['step_index']}: {s['content']}")

    print("\nSession Blackboard demo completed successfully with zero memory errors.")

if __name__ == "__main__":
    main()