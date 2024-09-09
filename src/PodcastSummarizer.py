import os
import yt_dlp
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import tiktoken

class PodcastSummarizer:
    def __init__(self):
        self.openai_api_key = os.getenv('JACO_OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        openai.api_key = self.openai_api_key
        self.GPT_MODEL = "gpt-4o-mini"

    def get_youtube_transcript(self, video_url):
        try:
            # Extract video ID from URL
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_id = info['id']

            # Get transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = ' '.join([entry['text'] for entry in transcript])
            return full_transcript
        except Exception as e:
            print(f"Error getting YouTube transcript: {str(e)}")
            return None

    def summarize_text(self, text):
        try:
            response = openai.chat.completions.create(
                model=self.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes podcast transcripts."},
                    {"role": "user", "content": f"Please summarize the following podcast transcript:\n\n{text}"}
                ],
            )
            summary = response.choices[0].message.content
            # Save the summary to a file in the data directory
            try:
                # Generate a filename based on the current timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"../data/summary_{timestamp}.txt"
                
                # Write the summary to the file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(summary)
                
                print(f"Summary saved to {filename}")
            except Exception as e:
                print(f"Error saving summary to file: {str(e)}")
            return summary
        
        except Exception as e:
            print(f"Error summarizing text: {str(e)}")
            return None

    def summarize_podcast(self, video_url):
        transcript = self.get_youtube_transcript(video_url)

        def num_tokens_from_string(string: str, encoding_name: str) -> int:
            encoding = tiktoken.get_encoding(encoding_name)
            num_tokens = len(encoding.encode(string))
            return num_tokens

        # Use 'cl100k_base' for GPT-4 models
        token_count = num_tokens_from_string(transcript, "cl100k_base")
        print(f"Token count: {token_count}")

        if transcript:
            summary = self.summarize_text(transcript)
            if summary:
                return summary
            else:
                return "Failed to summarize the podcast."
        else:
            return "Failed to get the podcast transcript."

summarizer = PodcastSummarizer()
summary = summarizer.summarize_podcast("https://www.youtube.com/watch?v=jSqCL7Npln0&t=355s")
print(summary)
