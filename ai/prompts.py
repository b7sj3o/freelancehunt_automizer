BASE_PROMPT = """
Hi!  
You will write application messages for freelance projects on my behalf.  
I will provide you only the **project description**.

### About our agency:
- Name: Netly  
- Focus: creating websites and web applications
- Tech stack: Next.js, React, TailwindCSS, Python, FastAPI, Flask, PostgreSQL, Docker, AWS  
- We do full frontend, backend, API integrations, and admin panels
- use "\n" for new lines
- Website: https://netly.pp.ua  
- Hourly rate: $10/hour (if requested)

### Task:
1. Based on the project description, generate a **professional and concise application message** for the client.  
   - Use information about our agency and tech stack.  
   - The **message must be in Ukrainian**.  
   - Be structured, clear, and without fluff.  
   - Do NOT use markup, bold, bullet points formatting, or placeholders like [Ваше ім’я].  
   - Do NOT include formal sign-offs or extra details about Docker/AWS unless specifically relevant.  
   - At the end, add only: 
     "Наш сайт: https://netly.pp.ua\nБуду радий обговорити деталі."

2. Return only the plain text message.

Project description:
{project_description}
"""
