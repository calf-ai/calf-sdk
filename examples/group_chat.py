"""
Multi-agent brainstorming with round-robin coordination.

Demonstrates:
- Multiple agents with specialized tools
- GroupChat for round-robin turn management
- Automatic stop condition (all agents skip in same round)
- Event-driven multi-agent coordination

Run:
    uv run examples/group_chat.py
"""

import asyncio

from calf import Calf, Agent, GroupChat, tool, RunContext


calf = Calf()


# ============== TOOLS ==============


@calf.tool
async def brainstorm_ideas(ctx: RunContext, topic: str) -> str:
    """Generate creative ideas and possibilities for a topic.

    Args:
        topic: The subject to brainstorm about
    """
    await asyncio.sleep(0.3)  # Simulate thinking
    return f"Brainstormed creative directions for: {topic}"


@calf.tool
async def assess_feasibility(ctx: RunContext, idea: str) -> str:
    """Assess the practical feasibility of an idea.

    Args:
        idea: The idea or proposal to evaluate
    """
    await asyncio.sleep(0.3)  # Simulate analysis
    return f"Feasibility assessment complete for: {idea}"


@calf.tool
async def find_risks(ctx: RunContext, proposal: str) -> str:
    """Identify potential risks and challenges with a proposal.

    Args:
        proposal: The proposal to analyze for risks
    """
    await asyncio.sleep(0.3)  # Simulate analysis
    return f"Risk analysis complete for: {proposal}"


# ============== AGENTS ==============


visionary = Agent(
    name="visionary",
    model="gpt-4o-mini",
    tools=[brainstorm_ideas],
    system_prompt="""You are The Visionary in a startup brainstorming session.

Your role: Generate creative ideas, see the big picture, inspire possibilities.

Guidelines:
- Use your brainstorm_ideas tool when exploring new directions
- Build on what others say, don't just repeat points
- Keep responses concise (2-3 sentences)
- Say "SKIP" if you have nothing new to add this round""",
)


pragmatist = Agent(
    name="pragmatist",
    model="gpt-4o-mini",
    tools=[assess_feasibility],
    system_prompt="""You are The Pragmatist in a startup brainstorming session.

Your role: Ground ideas in reality, assess feasibility, focus on execution.

Guidelines:
- Use your assess_feasibility tool when evaluating concrete proposals
- Offer constructive alternatives, not just criticism
- Keep responses concise (2-3 sentences)
- Say "SKIP" if you have nothing new to add this round""",
)


critic = Agent(
    name="critic",
    model="gpt-4o-mini",
    tools=[find_risks],
    system_prompt="""\
You are The Devil's Advocate in a startup brainstorming session.

Your role: Challenge assumptions, find blind spots, stress-test ideas.

Guidelines:
- Use your find_risks tool when analyzing proposals
- Be constructively critical, not just negative
- Keep responses concise (2-3 sentences)
- Say "SKIP" if risks have been addressed or you have nothing new to add""",
)


# ============== GROUP CHAT ==============


chat = GroupChat(
    name="brainstorm",
    agents=[visionary, pragmatist, critic],
)
chat.register(calf)


# ============== MAIN ==============


async def main() -> None:
    print("=" * 60)
    print("Group Chat: Startup Brainstorming Session")
    print("=" * 60)
    print("\nParticipants: Visionary, Pragmatist, Critic")
    print("Format: Round-robin turns")
    print("Stop condition: All agents skip in the same round")
    print("=" * 60)

    topic = "Brainstorm an AI startup idea for pet owners"

    print(f"\nTopic: {topic}\n")
    print("-" * 60)

    async for msg in chat.run_stream(topic):
        print(f"{msg.agent}: {msg.content}\n")

    print("-" * 60)
    print("Brainstorm complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
