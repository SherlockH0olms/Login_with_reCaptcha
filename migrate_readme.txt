How to get Google reCAPTCHA keys:
1. Go to https://www.google.com/recaptcha/admin
2. Register a site (choose reCAPTCHA v2 -> "I'm not a robot" Checkbox)
3. Add your domain (for local testing, you can add 'localhost')
4. You'll get SITE_KEY and SECRET_KEY. Put them into .env or environment variables.
