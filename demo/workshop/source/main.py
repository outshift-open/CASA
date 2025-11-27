import aiohttp
import uvicorn
import os
from fastapi import FastAPI
from pydantic import BaseModel

from identity_auth_server import sdk

app = FastAPI()

AGENT_CHAT_URL = os.getenv("AGENT_CHAT_URL", "http://localhost:8082/chat")
AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL", "http://localhost:8000")
CLIENT_BASE_URL = os.getenv("TRUSTED_CLIENT_BASE_URL", "http://localhost:3999")

CLIENT_METADATA = {
    "client_id": f"{CLIENT_BASE_URL}/oauth/client-metadata.json",
    "client_name": "Financial Assistant",
    "grant_types": ["client_credentials"],
    "response_types": ["token"],
    "token_endpoint_auth_method": "private_key_jwt",
    "jwks_uri": "https://identity-service/v1alpha1/issuer/keycloak/.well-known/jwks.json",
    "vc+jwt": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjNlZDI2NWU3LTE4ZTItNDQ2Ni05MDU2LTk0M2I4NDQ1NGE4NiJ9.eyJjb250ZXh0IjpbImh0dHBzOi8vd3d3LnczLm9yZy9ucy9jcmVkZW50aWFscy92MiIsImh0dHBzOi8vd3d3LnczLm9yZy9ucy9jcmVkZW50aWFscy9leGFtcGxlcy92MiJdLCJ0eXBlIjpbIkJBREdFX1RZUEVfQUdFTlRfQkFER0UiXSwiaXNzdWVyIjoic3NvLTE1OGM0ODlmLnNzby5kdW9zZWN1cml0eS5jb20iLCJjcmVkZW50aWFsU3ViamVjdCI6eyJpZCI6IkRVTy1iZmMwYTU0My01ZjhhLTQzNjEtODUwNy0yOTUyODRmMWE1NmMiLCJiYWRnZSI6IntcbiAgXCJzY2hlbWFfdmVyc2lvblwiOiBcInYxLjAuMFwiLFxuICBcIm5hbWVcIjogXCJhZ250Y3kvZmluYW5jaWFsLWFzc2lzdGFudFwiLFxuICBcInZlcnNpb25cIjogXCJ2MS4wLjBcIixcbiAgXCJkZXNjcmlwdGlvblwiOiBcIkEgbXVsdGktZnVuY3Rpb25hbCBmaW5hbmNpYWwgYXNzaXN0YW50IGRlc2lnbmVkIGhlbHAgd2l0aCBjdXJyZW5jeSBjb252ZXJzaW9uLlwiLFxuICBcImF1dGhvcnNcIjogW1wiQ2lzY28gU3lzdGVtcyBJbmMuXCJdLFxuICBcImNyZWF0ZWRfYXRcIjogXCIyMDI1LTA0LTI0VDEyOjAwOjAwWlwiLFxuICBcImFubm90YXRpb25zXCI6IHtcbiAgICBcInR5cGVcIjogXCJsYW5nZ3JhcGhcIlxuICB9LFxuICBcInNraWxsc1wiOiBbXG4gICAge1xuICAgICAgXCJjYXRlZ29yeV91aWRcIjogMSxcbiAgICAgIFwiY2xhc3NfdWlkXCI6IDEwMjA0LFxuICAgICAgXCJjYXRlZ29yeV9uYW1lXCI6IFwiTmF0dXJhbCBMYW5ndWFnZSBQcm9jZXNzaW5nXCIsXG4gICAgICBcImNsYXNzX25hbWVcIjogXCJEaWFsb2d1ZSBHZW5lcmF0aW9uXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwiY2F0ZWdvcnlfdWlkXCI6IDEsXG4gICAgICBcImNsYXNzX3VpZFwiOiAxMDIwMSxcbiAgICAgIFwiY2F0ZWdvcnlfbmFtZVwiOiBcIk5hdHVyYWwgTGFuZ3VhZ2UgUHJvY2Vzc2luZ1wiLFxuICAgICAgXCJjbGFzc19uYW1lXCI6IFwiVGV4dCBDb21wbGV0aW9uXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwiY2F0ZWdvcnlfdWlkXCI6IDEsXG4gICAgICBcImNsYXNzX3VpZFwiOiAxMDIwMyxcbiAgICAgIFwiY2F0ZWdvcnlfbmFtZVwiOiBcIk5hdHVyYWwgTGFuZ3VhZ2UgUHJvY2Vzc2luZ1wiLFxuICAgICAgXCJjbGFzc19uYW1lXCI6IFwiVGV4dCBQYXJhcGhyYXNpbmdcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJjYXRlZ29yeV91aWRcIjogMSxcbiAgICAgIFwiY2xhc3NfdWlkXCI6IDEwMzAzLFxuICAgICAgXCJjYXRlZ29yeV9uYW1lXCI6IFwiTmF0dXJhbCBMYW5ndWFnZSBQcm9jZXNzaW5nXCIsXG4gICAgICBcImNsYXNzX25hbWVcIjogXCJLbm93bGVkZ2UgU3ludGhlc2lzXCJcbiAgICB9LFxuICAgIHtcbiAgICAgIFwiY2F0ZWdvcnlfdWlkXCI6IDEsXG4gICAgICBcImNsYXNzX3VpZFwiOiAxMDIwNixcbiAgICAgIFwiY2F0ZWdvcnlfbmFtZVwiOiBcIk5hdHVyYWwgTGFuZ3VhZ2UgUHJvY2Vzc2luZ1wiLFxuICAgICAgXCJjbGFzc19uYW1lXCI6IFwiVGV4dCBTdHlsZSBUcmFuc2ZlclwiXG4gICAgfSxcbiAgICB7XG4gICAgICBcImNhdGVnb3J5X3VpZFwiOiAxLFxuICAgICAgXCJjbGFzc191aWRcIjogMTA2MDIsXG4gICAgICBcImNhdGVnb3J5X25hbWVcIjogXCJOYXR1cmFsIExhbmd1YWdlIFByb2Nlc3NpbmdcIixcbiAgICAgIFwiY2xhc3NfbmFtZVwiOiBcIlRvbmUgYW5kIFN0eWxlIEFkanVzdG1lbnRcIlxuICAgIH1cbiAgXSxcbiAgXCJsb2NhdG9yc1wiOiBbXG4gICAge1xuICAgICAgXCJ0eXBlXCI6IFwic291cmNlLWNvZGVcIixcbiAgICAgIFwidXJsXCI6IFwiaHR0cHM6Ly9naXRodWIuY29tL2FnbnRjeS9hZ2VudGljLWFwcHMvdHJlZS9tYWluL2ZpbmFuY2lhbC1hc3Npc3RhbnRcIlxuICAgIH0sXG4gICAge1xuICAgICAgXCJ0eXBlXCI6IFwicHl0aG9uLXBhY2thZ2VcIixcbiAgICAgIFwidXJsXCI6IFwiaHR0cHM6Ly9naXRodWIuY29tL2FnbnRjeS9hZ2VudGljLWFwcHMvdHJlZS9tYWluL2ZpbmFuY2lhbC1hc3Npc3RhbnQvcHlwcm9qZWN0LnRvbWxcIlxuICAgIH1cbiAgXSxcbiAgXCJleHRlbnNpb25zXCI6IFtcbiAgICB7XG4gICAgICBcIm5hbWVcIjogXCJzY2hlbWEub2FzZi5hZ250Y3kub3JnL2ZlYXR1cmVzL3J1bnRpbWUvZnJhbWV3b3JrXCIsXG4gICAgICBcInZlcnNpb25cIjogXCJ2MC4wLjBcIixcbiAgICAgIFwiZGF0YVwiOiB7XG4gICAgICAgIFwic2JvbVwiOiB7XG4gICAgICAgICAgXCJuYW1lXCI6IFwiZmluYW5jaWFsX2Fzc2lzdGFudFwiLFxuICAgICAgICAgIFwicGFja2FnZXNcIjogW1xuICAgICAgICAgICAge1xuICAgICAgICAgICAgICBcIm5hbWVcIjogXCJweXRob24tZG90ZW52XCIsXG4gICAgICAgICAgICAgIFwidmVyc2lvblwiOiBcIl4xLjAuMVwiXG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAge1xuICAgICAgICAgICAgICBcIm5hbWVcIjogXCJsYW5nZ3JhcGhcIixcbiAgICAgICAgICAgICAgXCJ2ZXJzaW9uXCI6IFwiXjAuMy41XCJcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIFwibmFtZVwiOiBcImxhbmdjaGFpbi1vcGVuYWlcIixcbiAgICAgICAgICAgICAgXCJ2ZXJzaW9uXCI6IFwiXjAuMy44XCJcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIFwibmFtZVwiOiBcImxhbmdjaGFpblwiLFxuICAgICAgICAgICAgICBcInZlcnNpb25cIjogXCJeMC4zLjIwXCJcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIFwibmFtZVwiOiBcImFnbnRjeS1hY3BcIixcbiAgICAgICAgICAgICAgXCJ2ZXJzaW9uXCI6IFwiMS4xLjJcIlxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgXCJuYW1lXCI6IFwiZ3JhZGlvXCIsXG4gICAgICAgICAgICAgIFwidmVyc2lvblwiOiBcIl41LjIzLjFcIlxuICAgICAgICAgICAgfVxuICAgICAgICAgIF1cbiAgICAgICAgfVxuICAgICAgfVxuICAgIH0sXG4gICAge1xuICAgICAgXCJuYW1lXCI6IFwic2NoZW1hLm9hc2YuYWdudGN5Lm9yZy9mZWF0dXJlcy9ydW50aW1lL2xhbmd1YWdlXCIsXG4gICAgICBcInZlcnNpb25cIjogXCJ2MC4wLjBcIixcbiAgICAgIFwiZGF0YVwiOiB7XG4gICAgICAgIFwidHlwZVwiOiBcInB5dGhvblwiLFxuICAgICAgICBcInZlcnNpb25cIjogXCJcdTAwM2U9My4xMCxcdTAwM2M0LjBcIlxuICAgICAgfVxuICAgIH1cbiAgXSxcbiAgXCJzaWduYXR1cmVcIjoge1xuICAgIFwiYWxnb3JpdGhtXCI6IFwiU0hBMl8yNTZcIixcbiAgICBcInNpZ25hdHVyZVwiOiBcIk1FVUNJR1ZYbnByVUlsMXhEcFNBVGQwSW4vdG04WmsrbmZzZ3M4QkRyMCtTQldZakFpRUF3QVpJN2RQTUdYMGM0TFAzR2kyeGdsMEhWMGg0UVR3OGZPSmNRZGYzbHdJPVwiXG4gIH1cbn1cbiJ9LCJpZCI6ImFiZDkwZjU5LWNkZGItNGY2OC05NjExLWFkMjUxZGM0ZDQyZCIsImlzc3VhbmNlRGF0ZSI6IjIwMjUtMDgtMDRUMDc6NTA6MDNaIn0.lsyF_wgYnY2Z7hktCWGWLgzbMHVplRwTS_ghYj8_uG1GiHCYXh6tDPFdMsuGFi6--aboyr7fnBXx8Dz0-KLQb6j_yFZw7dlzXTZvNuHZu_TPFc613GZW8vQ5Z4Riqc-8hi_2JwM7BlJJ2M9Vmmv30YTnrumZVqgu4OF_P_R780fKl3gbH4XFW5ZJe7hUJqnoEMaFUnKgQ1TO3MASIBn7yeo29xtd_hvlmHzjOQC761GSrywYrwZqwRtjqWYv6oU7lA0iO4Mq3vev2gLH83Q8vUmBkXYrug-deJMPjtK9CodFZ3GgiMyygjgvPvbPi_kmZFwvAZ94rnk1CSeToj28IQ",
}


class ChatRequest(BaseModel):
    content: str


async def send_chat_request(user_content: str, bearer_token: str = None):
    """Send HTTP POST request to chat endpoint with user content"""
    url = AGENT_CHAT_URL

    # Prepare the payload
    payload = {"content": user_content}

    # Prepare headers
    headers = {"Content-Type": "application/json"}
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    print(f"Error {response.status}: {error_text}")
                    return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None


@app.get("/oauth/client-metadata.json")
async def get_client_metadata():
    """Exposes the client metadata as a JSON response."""
    return CLIENT_METADATA


@app.post("/process")
async def process_chat(request: ChatRequest):
    """Process chat request with authentication and authorization"""
    user_content = request.content

    async with sdk.AsyncIdentityAuthClient(AUTH_SERVER_URL) as client:
        source_app_token = await client.get_source_app_call_token(
            input=user_content,
            grant_type="client_credentials",
            client_id=f"{CLIENT_BASE_URL}/oauth/client-metadata.json",
            client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            client_assertion="eyJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1In0.eyJpc3MiOiJ5b3VyLWNsaWVudC1pZCIsInN1YiI6InlvdXItY2xpZW50LWlkIiwiYXVkIjoiaHR0cHM6Ly9hdXRoLmV4YW1wbGUuY29tL29hdXRoMi90b2tlbiIsImlhdCI6MTcyNjUxMzkyNywiZXhwIjoxNzI2NTE0MjI3LCJqdGkiOiIxNzI2NTEzOTI3OTYxMDAwMCJ9",
        )

        await client.create_source_app_call(
            payload=sdk.types.SourceAppCallInput(token=source_app_token, input=user_content)
        )

        response = await send_chat_request(user_content, source_app_token)

        await client.create_source_app_response(
            payload=sdk.types.SourceAppResponseInput(
                source_app_call_token=source_app_token, token=source_app_token, output=response.get("response", "")
            )
        )

        return {"status": "success", "response": response}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3999)
