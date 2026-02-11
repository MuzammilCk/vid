"""
AI Prompt Templates for VidBrain AI
Stores all prompt templates for video classification and analysis
"""

CLASSIFICATION_PROMPT = """You are a video classification AI. Analyze the following YouTube video data and classify it into EXACTLY ONE of these categories:

CATEGORIES:
- movie_list: Videos listing, ranking, or recommending movies/films
- song_list: Videos listing, compiling, or ranking songs/music
- comedy: Stand-up comedy, skits, funny videos, comedy sketches
- recipe: Cooking tutorials, recipe demonstrations, food preparation
- education: Educational content, lectures, explainers, documentaries
- product_review: Product reviews, unboxing, tech reviews, comparisons
- travel: Travel vlogs, destination guides, travel tips
- news: News coverage, current events, journalism
- fitness: Workout videos, exercise routines, fitness guides
- podcast: Podcast recordings, interviews, long-form discussions
- tutorial: How-to guides, software tutorials, DIY projects
- gaming: Gaming content, walkthroughs, let's plays, esports
- vlog: Personal vlogs, day-in-the-life, lifestyle content
- unknown: Doesn't clearly fit any category above

VIDEO DATA:
Title: {title}
Channel: {channel}
Description: {description}
Tags: {tags}
YouTube Category ID: {category_id}
Duration: {duration} seconds
View Count: {view_count}
Upload Date: {upload_date}

Transcript (first 3000 chars):
{transcript}

Top Comments:
{comments}

INSTRUCTIONS:
1. Consider ALL provided data points
2. Weight transcript/captions heavily (actual content matters most)
3. Be confident - only use "unknown" if truly ambiguous
4. Provide clear reasoning based on concrete evidence

RESPOND IN THIS EXACT JSON FORMAT (no markdown, no code blocks, no extra text):
{{
    "category": "one_of_the_categories_above",
    "confidence": 0.95,
    "sub_category": "optional more specific label",
    "reasoning": "brief explanation citing specific evidence from the data",
    "alternative_categories": ["backup_option_1", "backup_option_2"]
}}"""

CLASSIFICATION_PROMPT_WITH_IMAGES = """You are a video classification AI with visual analysis capabilities. Analyze the YouTube video data AND the provided video frames.

CATEGORIES:
- movie_list: Videos listing, ranking, or recommending movies/films
- song_list: Videos listing, compiling, or ranking songs/music
- comedy: Stand-up comedy, skits, funny videos, comedy sketches
- recipe: Cooking tutorials, recipe demonstrations, food preparation
- education: Educational content, lectures, explainers, documentaries
- product_review: Product reviews, unboxing, tech reviews, comparisons
- travel: Travel vlogs, destination guides, travel tips
- news: News coverage, current events, journalism
- fitness: Workout videos, exercise routines, fitness guides
- podcast: Podcast recordings, interviews, long-form discussions
- tutorial: How-to guides, software tutorials, DIY projects
- gaming: Gaming content, walkthroughs, let's plays, esports
- vlog: Personal vlogs, day-in-the-life, lifestyle content
- unknown: Doesn't clearly fit any category above

VIDEO DATA:
Title: {title}
Channel: {channel}
Description: {description}
Tags: {tags}
YouTube Category ID: {category_id}
Duration: {duration} seconds
View Count: {view_count}
Upload Date: {upload_date}

Transcript (first 3000 chars):
{transcript}

Top Comments:
{comments}

KEY FRAMES PROVIDED:
{num_frames} frames from the video are attached. Analyze these for:
- Visual content type (talking head, product, food, scenery, etc.)
- Text overlays or graphics
- Setting/environment
- Production quality indicators

Use both textual data AND visual evidence to make your classification.

INSTRUCTIONS:
1. Consider ALL provided data points (text AND images)
2. Weight transcript/captions heavily (actual content matters most)
3. Use visual frames to validate your classification
4. Be confident - only use "unknown" if truly ambiguous
5. Provide clear reasoning based on concrete evidence

RESPOND IN THIS EXACT JSON FORMAT (no markdown, no code blocks, no extra text):
{{
    "category": "one_of_the_categories_above",
    "confidence": 0.95,
    "sub_category": "optional more specific label",
    "reasoning": "brief explanation citing specific evidence from the data",
    "alternative_categories": ["backup_option_1", "backup_option_2"]
}}"""
