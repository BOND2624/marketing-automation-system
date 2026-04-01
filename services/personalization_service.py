"""Personalization Service - Ollama-powered content suggestions for multi-platform posting."""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Platform identifiers (lowercase)
PLATFORMS = {"youtube", "instagram", "facebook"}


def _get_llm():
    """Get Ollama LLM instance."""
    try:
        from langchain_ollama import OllamaLLM as Ollama
    except ImportError:
        try:
            from langchain_community.llms import Ollama
        except ImportError:
            from langchain.llms import Ollama

    if settings.llm_provider == "ollama":
        return Ollama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            timeout=60,
        )
    return Ollama(model="llama3", timeout=60)


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from LLM response (may be wrapped in markdown)."""
    if not text or not text.strip():
        return None
    text = text.strip()
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try to find JSON in markdown code block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    # Try to find {...} in text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _extract_json_array(text: str) -> Optional[List[Any]]:
    """Extract JSON array from LLM response."""
    if not text or not text.strip():
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


class PersonalizationService:
    """
    Ollama-powered content personalization for multi-platform campaigns.
    Generates titles, captions, tags, and hashtags tailored to each platform.
    """

    def __init__(self, llm=None):
        """
        Initialize PersonalizationService.

        Args:
            llm: Optional LLM instance. Uses Ollama from config if not provided.
        """
        self.llm = llm or _get_llm()

    def suggest_titles(
        self,
        topic: str,
        product_name: Optional[str] = None,
        count: int = 5,
        platform: Optional[str] = None,
    ) -> List[str]:
        """
        Generate title suggestions for the given topic.

        Args:
            topic: Main topic or title idea
            product_name: Optional product/brand name
            count: Number of titles to generate
            platform: Optional platform (youtube, instagram, facebook)

        Returns:
            List of title strings
        """
        platform_hint = f" for {platform}" if platform else ""
        product_hint = f" Product/brand: {product_name}." if product_name else ""
        prompt = f"""You are a marketing copywriter. Generate exactly {count} catchy titles{platform_hint}.

Topic: {topic}
{product_hint}

Requirements:
- Each title under 60 characters
- Include a hook or benefit
- No clickbait
- Output ONLY a JSON array of strings, e.g. ["title1", "title2"]
- No other text, no explanation"""

        try:
            response = self.llm.invoke(prompt)
            response_text = getattr(response, "content", response) if response else ""
            response_text = response_text if isinstance(response_text, str) else str(response)
            titles = _extract_json_array(response_text)
            if titles and isinstance(titles, list):
                return [str(t).strip()[:60] for t in titles if t][:count]
        except Exception as e:
            logger.warning(f"Title suggestion failed: {e}")
        return [topic[:60]]  # Fallback to topic

    def suggest_caption(
        self,
        topic: str,
        platform: str,
        tone: str = "casual",
        include_hashtags: bool = True,
    ) -> str:
        """
        Generate a caption for the given platform.

        Args:
            topic: Main topic or message
            platform: youtube, instagram, or facebook
            tone: casual, professional, or fun
            include_hashtags: Whether to include hashtags (Instagram)

        Returns:
            Caption string
        """
        platform_rules = {
            "instagram": "Short, engaging, 1-2 sentences. Use 3-5 hashtags at the end.",
            "facebook": "Conversational, shareable, include a call-to-action.",
            "youtube": "Can be longer, descriptive, SEO-friendly.",
        }
        rules = platform_rules.get(platform.lower(), "Engaging and clear.")
        hashtag_instruction = " Include 3-5 relevant hashtags at the end." if include_hashtags and platform.lower() == "instagram" else ""

        prompt = f"""Write a social media caption for {platform}.

Topic: {topic}
Tone: {tone}
{rules}{hashtag_instruction}

Output ONLY the caption text. No quotes, no explanation, no JSON. Just the caption."""

        try:
            response = self.llm.invoke(prompt)
            caption = getattr(response, "content", response) if response else ""
            caption = caption if isinstance(caption, str) else str(caption)
            return caption.strip().strip('"').strip("'")[:2200]  # Instagram caption limit
        except Exception as e:
            logger.warning(f"Caption suggestion failed: {e}")
        return topic[:500]  # Fallback

    def suggest_tags(
        self,
        topic: str,
        platform: str,
        count: int = 10,
    ) -> Dict[str, List[str]]:
        """
        Suggest tags and hashtags for the topic.

        Args:
            topic: Main topic
            platform: youtube, instagram, or facebook
            count: Number of tags/hashtags

        Returns:
            Dict with 'tags' (YouTube-style) and 'hashtags' (Instagram-style)
        """
        prompt = f"""Suggest {count} relevant tags and hashtags for a social media post about: {topic}
Platform: {platform}

Output ONLY a JSON object with two keys:
- "tags": array of strings (no # symbol, for YouTube)
- "hashtags": array of strings (with # symbol, for Instagram)

Example: {{"tags": ["coffee", "morning"], "hashtags": ["#CoffeeLovers", "#MorningRitual"]}}
No other text."""

        try:
            response = self.llm.invoke(prompt)
            response_text = getattr(response, "content", response) if response else ""
            response_text = response_text if isinstance(response_text, str) else str(response_text)
            data = _extract_json(response_text)
            if data:
                tags = data.get("tags", [])
                hashtags = data.get("hashtags", [])
                if isinstance(tags, list):
                    tags = [str(t).strip() for t in tags if t][:count]
                else:
                    tags = []
                if isinstance(hashtags, list):
                    hashtags = [str(h).strip() if str(h).startswith("#") else f"#{str(h).strip()}" for h in hashtags if h][:count]
                else:
                    hashtags = []
                return {"tags": tags, "hashtags": hashtags}
        except Exception as e:
            logger.warning(f"Tag suggestion failed: {e}")
        return {"tags": [], "hashtags": []}

    def personalize_for_channels(
        self,
        base_title: str,
        channels: List[str],
        tone: str = "casual",
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate personalized content for each selected platform from one base title/topic.

        Args:
            base_title: User's title or topic
            channels: List of platform names (youtube, instagram, facebook)
            tone: casual, professional, or fun

        Returns:
            Dict mapping platform -> {title, caption, tags, hashtags}
        """
        result: Dict[str, Dict[str, Any]] = {}
        channels = [c.lower() for c in channels if c.lower() in PLATFORMS]

        for platform in channels:
            platform_data: Dict[str, Any] = {}

            # Title (used for YouTube, or as base for others)
            titles = self.suggest_titles(base_title, platform=platform, count=3)
            platform_data["title"] = titles[0] if titles else base_title

            # Caption
            platform_data["caption"] = self.suggest_caption(
                base_title, platform, tone=tone, include_hashtags=(platform == "instagram")
            )

            # Tags and hashtags
            tag_data = self.suggest_tags(base_title, platform, count=8)
            platform_data["tags"] = tag_data.get("tags", [])
            platform_data["hashtags"] = tag_data.get("hashtags", [])

            # For Instagram: combine caption with hashtags if not already present
            if platform == "instagram" and platform_data["hashtags"]:
                caption = platform_data["caption"]
                hashtag_str = " ".join(platform_data["hashtags"])
                if "#" not in caption:
                    platform_data["content"] = f"{caption}\n\n{hashtag_str}"
                else:
                    platform_data["content"] = caption
            else:
                platform_data["content"] = platform_data["caption"]

            result[platform] = platform_data

        return result

    def _suggest_for_publish_batched(
        self,
        seed: str,
        platform: str,
        tone: str = "casual",
    ) -> Dict[str, Any]:
        """
        Single LLM round-trip for Social Publish (much faster than 3 sequential calls).
        """
        platform = platform.lower()
        rules = {
            "instagram": (
                "Caption: 1-2 short engaging sentences. Put 3-5 hashtags only in the "
                '"hashtags" array (each string starts with #), not duplicated in caption unless natural.'
            ),
            "facebook": "Post text: conversational, shareable, with a soft call-to-action.",
            "youtube": (
                "Caption field = full video description (SEO-friendly, multiple sentences OK). "
                '"tags": 5-12 short keywords without # for YouTube search. "hashtags" can be [].'
            ),
        }
        rule = rules.get(platform, "Engaging and clear.")

        prompt = f"""You are a marketing copywriter. Produce publish-ready copy in ONE JSON object.

User notes/topic:
{seed}

Platform: {platform}
Tone: {tone}
{rule}

Output ONLY valid JSON (no markdown fences) with exactly these keys:
- "title": string, max 70 characters (YouTube video title; for IG/FB a short headline is fine)
- "caption": string (main body: IG/FB post text, or YouTube description per rules above)
- "tags": array of strings without # (mainly for YouTube; use [] if none)
- "hashtags": array of strings, each starting with # (for Instagram; [] if not needed)

JSON object only."""

        response = self.llm.invoke(prompt)
        text = getattr(response, "content", response) if response else ""
        text = text if isinstance(text, str) else str(text)
        data = _extract_json(text)
        if not data or not isinstance(data, dict):
            raise ValueError("batched LLM response was not valid JSON")

        title = str(data.get("title") or "").strip()[:100] or seed[:100]
        caption = str(data.get("caption") or "").strip()[:2200]

        raw_tags = data.get("tags", [])
        tags: List[str] = []
        if isinstance(raw_tags, list):
            tags = [str(t).strip() for t in raw_tags if t][:15]

        raw_ht = data.get("hashtags", [])
        hashtags: List[str] = []
        if isinstance(raw_ht, list):
            for h in raw_ht:
                if not h:
                    continue
                s = str(h).strip()
                if not s.startswith("#"):
                    s = f"#{s}"
                hashtags.append(s)
            hashtags = hashtags[:15]

        if platform == "instagram" and hashtags:
            hashtag_str = " ".join(hashtags)
            if "#" not in caption:
                body = f"{caption}\n\n{hashtag_str}".strip()
            else:
                body = caption
        else:
            body = caption

        return {
            "title": title,
            "description": body,
            "body": body,
            "tags": tags,
            "hashtags": hashtags,
        }

    def suggest_for_publish(
        self,
        user_input: str,
        platform: str,
        tone: str = "casual",
    ) -> Dict[str, Any]:
        """
        Single-platform bundle for the Social Publish UI: title, body text, tags, hashtags.

        Uses one Ollama call when possible; falls back to the 3-call pipeline if JSON parse fails.

        Args:
            user_input: Any seed text the user entered (title, caption, description, notes).
            platform: youtube | instagram | facebook
            tone: casual | professional | fun

        Returns:
            Dict with title, description, body, tags, hashtags (lists for tags/hashtags).
        """
        platform = platform.lower().strip()
        if platform not in PLATFORMS:
            raise ValueError(f"Invalid platform: {platform}. Use one of: {', '.join(sorted(PLATFORMS))}")
        seed = (user_input or "").strip()
        if not seed:
            raise ValueError("user_input is required")

        try:
            return self._suggest_for_publish_batched(seed, platform, tone=tone)
        except Exception as e:
            logger.warning(
                "Batched personalization failed (%s); falling back to 3-call pipeline", e
            )
            personalized = self.personalize_for_channels(seed, channels=[platform], tone=tone)
            row = personalized.get(platform) or {}

            caption = (row.get("caption") or "").strip()
            body = (row.get("content") or caption).strip()
            title = (row.get("title") or "").strip() or seed[:100]

            tags = row.get("tags") or []
            hashtags = row.get("hashtags") or []
            if not isinstance(tags, list):
                tags = []
            if not isinstance(hashtags, list):
                hashtags = []

            return {
                "title": title,
                "description": body,
                "body": body,
                "tags": [str(t).strip() for t in tags if t],
                "hashtags": [str(h).strip() for h in hashtags if h],
            }
