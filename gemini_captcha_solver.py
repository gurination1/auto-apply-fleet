#!/usr/bin/env python3
"""
Autonomous Gemini-Powered Captcha Solver
Solves Google reCAPTCHA v2 / hCaptcha audio and visual challenges using Gemini Multimodal AI.
Also detects and organically solves Cloudflare Turnstile checkboxes.
"""

import os
import re
import json
import base64
import random
import requests
import time

def get_gemini_api_key():
    key = os.environ.get('GEMINI_API_KEY')
    if not key and os.path.exists('/root/local_env.sh'):
        try:
            with open('/root/local_env.sh') as f:
                for line in f:
                    if 'GEMINI_API_KEY=' in line and not '_KEYS' in line:
                        key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass
    return key

def solve_audio_challenge_with_gemini(audio_bytes):
    key = get_gemini_api_key()
    if not key:
        print("[-] GEMINI_API_KEY not configured for captcha solving.")
        return None

    try:
        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        payload = {
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "audio/mp3",
                            "data": b64_audio
                        }
                    },
                    {
                        "text": "Transcribe the exact spoken words or numbers from this captcha audio clip. Output ONLY the numbers/words without punctuation, markdown, or commentary."
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 30
            }
        }
        res = requests.post(url, json=payload, timeout=12)
        if res.status_code == 200:
            sol = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            # Clean non-alphanumeric except space
            sol_clean = re.sub(r'[^a-zA-Z0-9\s]', '', sol).strip()
            print(f"[+] Gemini Captcha Solver decoded audio: '{sol_clean}'")
            return sol_clean
        else:
            print(f"[-] Gemini API error: {res.status_code} - {res.text[:100]}")
    except Exception as e:
        print(f"[-] Gemini audio challenge exception: {e}")
    return None

def solve_turnstile_if_present(page):
    """
    Detects and organically clicks Cloudflare Turnstile iframes.
    """
    try:
        # Check for turnstile iframe
        turnstile_frame = page.frame_locator('iframe[src*="challenges.cloudflare.com"], iframe[src*="turnstile"]').first
        chk = turnstile_frame.locator('input[type="checkbox"], #challenge-stage, .cf-turnstile')
        if chk.count() > 0 and chk.first.is_visible():
            print("[*] Cloudflare Turnstile detected. Clicking organically...")
            box = chk.first.bounding_box()
            if box:
                page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2, steps=8)
                page.wait_for_timeout(random.randint(400, 800))
                page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
                page.wait_for_timeout(2500)
                return True
    except Exception:
        pass
    return False

def solve_recaptcha_v2_if_present(page):
    """
    Detects reCAPTCHA v2 challenge frames, switches to audio, and solves using Gemini.
    """
    try:
        # 1. Check for initial checkbox if visible
        anchor_frame = page.frame_locator('iframe[src*="recaptcha/api2/anchor"]').first
        recaptcha_anchor = anchor_frame.locator('#recaptcha-anchor').first
        if recaptcha_anchor.count() > 0 and recaptcha_anchor.is_visible():
            aria_checked = recaptcha_anchor.get_attribute('aria-checked')
            if aria_checked != 'true':
                print("[*] reCAPTCHA v2 anchor detected. Clicking checkbox...")
                recaptcha_anchor.click()
                page.wait_for_timeout(2000)

        # 2. Check for challenge popup iframe
        bframe = page.frame_locator('iframe[src*="recaptcha/api2/bframe"]').first
        audio_btn = bframe.locator('#recaptcha-audio-button').first
        if audio_btn.count() > 0 and audio_btn.is_visible():
            print("[*] reCAPTCHA challenge active. Switching to audio mode for Gemini solver...")
            audio_btn.click()
            page.wait_for_timeout(2500)

            # Get audio download link
            dl_link = bframe.locator('.rc-audiochallenge-tdownload-link').first
            audio_url = dl_link.get_attribute('href') if dl_link.count() > 0 else None
            if not audio_url:
                audio_src = bframe.locator('#audio-source').first
                audio_url = audio_src.get_attribute('src') if audio_src.count() > 0 else None

            if audio_url:
                print(f"[*] Downloading captcha audio payload: {audio_url[:45]}...")
                audio_resp = requests.get(audio_url, timeout=10)
                if audio_resp.status_code == 200:
                    solution = solve_audio_challenge_with_gemini(audio_resp.content)
                    if solution:
                        resp_input = bframe.locator('#audio-response').first
                        if resp_input.count() > 0:
                            resp_input.fill(solution)
                            page.wait_for_timeout(600)
                            verify_btn = bframe.locator('#recaptcha-verify-button').first
                            if verify_btn.count() > 0:
                                verify_btn.click()
                                page.wait_for_timeout(2500)
                                print("[+] reCAPTCHA audio challenge submitted with Gemini solution!")
                                return True
    except Exception as e:
        print(f"[-] reCAPTCHA solver notice: {e}")
    return False

def solve_visual_challenge_with_gemini(image_bytes, prompt_text):
    key = get_gemini_api_key()
    if not key:
        return None
    try:
        b64_img = base64.b64encode(image_bytes).decode('utf-8')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        system_instruction = (
            "You are an automated vision assistant for solving captcha verification tasks. "
            "Analyze the image showing a grid of tiles (numbered 1 through 9, ordered left-to-right, top-to-bottom). "
            f"Identify all tiles that match the challenge: '{prompt_text}'. "
            "Respond ONLY with a valid JSON array of matching tile indices (integers 1 to 9), for example: [1, 3, 7]. "
            "If none match or you are unsure, respond with []."
        )
        payload = {
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": b64_img
                        }
                    },
                    {
                        "text": system_instruction
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 60
            }
        }
        res = requests.post(url, json=payload, timeout=12)
        if res.status_code == 200:
            txt = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            m = re.search(r'\[[\d\s,]*\]', txt)
            if m:
                indices = json.loads(m.group(0))
                print(f"[+] Gemini Vision Captcha Solver picked tiles: {indices}")
                return indices
    except Exception as e:
        print(f"[-] Gemini vision solver error: {e}")
    return None

def solve_hcaptcha_if_present(page):
    """
    Detects and solves hCaptcha checkboxes and challenge popups using Gemini Vision & Audio.
    """
    try:
        # 1. Click checkbox if present
        hframe = page.frame_locator('iframe[src*="hcaptcha.com"]:not([src*="frame=challenge"]), iframe[data-hcaptcha-widget-id]').first
        chk = hframe.locator('#checkbox, [aria-haspopup="dialog"]').first
        if chk.count() > 0 and chk.is_visible():
            aria_checked = chk.get_attribute('aria-checked')
            if aria_checked != 'true':
                print("[*] hCaptcha checkbox detected. Clicking organically...")
                chk.click()
                page.wait_for_timeout(2500)

        # 2. Check for challenge popup iframe
        cframe = page.frame_locator('iframe[title*="hCaptcha challenge"], iframe[src*="hcaptcha.com"][src*="frame=challenge"]').first
        prompt_el = cframe.locator('.prompt-text, .prompt-text-desktop, .challenge-prompt, h2').first
        if prompt_el.count() > 0 and prompt_el.is_visible():
            prompt_text = prompt_el.inner_text().strip()
            print(f"[*] Active hCaptcha visual challenge detected: '{prompt_text}'")

            # Check for audio challenge alternative first
            audio_btn = cframe.locator('[aria-label*="audio" i], [title*="audio" i], .accessibility-btn').first
            if audio_btn.count() > 0 and audio_btn.is_visible():
                try:
                    audio_btn.click()
                    page.wait_for_timeout(2000)
                    audio_src_el = cframe.locator('audio source, audio').first
                    audio_url = audio_src_el.get_attribute('src') if audio_src_el.count() > 0 else None
                    if audio_url:
                        audio_resp = requests.get(audio_url, timeout=10)
                        if audio_resp.status_code == 200:
                            sol = solve_audio_challenge_with_gemini(audio_resp.content)
                            if sol:
                                inp = cframe.locator('input[type="text"], .response-input').first
                                if inp.count() > 0:
                                    inp.fill(sol)
                                    time.sleep(0.5)
                                    cframe.locator('.button-submit, [aria-label*="submit" i]').first.click()
                                    page.wait_for_timeout(3000)
                                    return True
                except Exception as e:
                    print(f"[-] hCaptcha audio challenge attempt notice: {e}")

            # Fallback to Gemini Multimodal visual solver
            try:
                challenge_box = cframe.locator('.challenge-container, body').first
                if challenge_box.count() > 0:
                    img_bytes = challenge_box.screenshot()
                    picked = solve_visual_challenge_with_gemini(img_bytes, prompt_text)
                    if picked:
                        tiles = cframe.locator('.task-image').all()
                        for p_idx in picked:
                            if 1 <= p_idx <= len(tiles):
                                tiles[p_idx - 1].click()
                                time.sleep(0.3)
                        submit_btn = cframe.locator('.button-submit, [aria-label*="submit" i]').first
                        if submit_btn.count() > 0:
                            submit_btn.click()
                            page.wait_for_timeout(3000)
                            return True
            except Exception as e:
                print(f"[-] hCaptcha visual solver attempt notice: {e}")
    except Exception:
        pass
    return False

def solve_all_captchas(page):
    """
    Master handler: checks and solves Turnstile, reCAPTCHA, and hCaptcha if present.
    """
    solved_turnstile = solve_turnstile_if_present(page)
    solved_recaptcha = solve_recaptcha_v2_if_present(page)
    solved_hcaptcha = solve_hcaptcha_if_present(page)
    return solved_turnstile or solved_recaptcha or solved_hcaptcha
