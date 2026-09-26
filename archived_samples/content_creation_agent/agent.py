from google.adk.agents  import ParallelAgent, LlmAgent

GEMINI_MODEL = "gemini-2.5-flash"

# Blog Content Agent
blog_agent = LlmAgent(
    name="BlogAgent",
    model=GEMINI_MODEL,
    instruction="""
You are a blogging expert. Suggest an engaging blog outline and content ideas 
on the topic based on user query.
Output as:
- Suggested Title
- Blog Outline (3-5 headings)
- Key Points under each heading
""",
    output_key="blog_content"
)

# YouTube Script Agent
youtube_agent = LlmAgent(
    name="YouTubeAgent",
    model=GEMINI_MODEL,
    instruction="""
You are a YouTube content strategist. Create:
1. A catchy title
2. A video script (short, conversational, < 2 min read)
3. A YouTube description (SEO-friendly, with 3-4 keywords)
for the topic based on user query.
""",
    output_key="youtube_content"
)

# Instagram Reels Agent
instagram_agent = LlmAgent(
    name="InstagramAgent",
    model=GEMINI_MODEL,
    instruction="""
You are a social media content creator. Suggest 3 Instagram Reel ideas for the topic based on user query.
For each reel, provide:
- Hook line
- Quick script idea
- Suggested hashtags
""",
    output_key="instagram_content"
)

# Parallel Content Creator Agent
content_creator_agent = ParallelAgent(
    name="ContentCreatorAgent",
    sub_agents=[blog_agent, youtube_agent, instagram_agent],
    description="Generates blog ideas, YouTube video content, and Instagram reel ideas in parallel."
)

# Root agent (for ADK compatibility)
root_agent = content_creator_agent
