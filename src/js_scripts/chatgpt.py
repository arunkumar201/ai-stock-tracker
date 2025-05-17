def get_chatgpt_scripts(prompt):
    escaped_prompt = prompt.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$').replace('\n', '\\n')
    
    script = f"""
    (function() {{
        // Helper function to wait for an element
        function waitForElement(selector, timeout = 15000) {{
            return new Promise((resolve, reject) => {{
                const element = document.querySelector(selector);
                if (element) return resolve(element);

                const observer = new MutationObserver(() => {{
                    const el = document.querySelector(selector);
                    if (el) {{
                        observer.disconnect();
                        resolve(el);
                    }}
                }});

                observer.observe(document.body, {{
                    childList: true,
                    subtree: true
                }});

                setTimeout(() => {{
                    observer.disconnect();
                    reject(new Error(`Timeout waiting for: ${{selector}}`));
                }}, timeout);
            }});
        }}

        // Handle cookie consent if it appears
        async function handleCookieConsent() {{
            try {{
                const selectors = [
                    'button[aria-label*="cookie" i]',
                    'button:contains("Accept")',
                    'button:contains("Accept all")',
                    'button:contains("Agree")',
                    'button:contains("I accept")',
                    'button[data-testid*="cookie"]',
                    '.cookie-consent-accept'
                ];

                for (const selector of selectors) {{
                    try {{
                        const button = document.querySelector(selector);
                        if (button && button.offsetParent !== null) {{
                            button.click();
                            console.log('Clicked cookie consent button:', selector);
                            await new Promise(resolve => setTimeout(resolve, 1000));
                            return true;
                        }}
                    }} catch (e) {{
                        console.log('Error clicking cookie button:', e);
                    }}
                }}
                return false;
            }} catch (error) {{
                console.log('Error in handleCookieConsent:', error);
                return false;
            }}
        }}

        // Enable web search if available
        async function enableWebSearch() {{
            try {{
                // Look for the search button
                const searchButton = await waitForElement('button[data-testid*="composer-button-search"], button[aria-label*="Search" i]');
                if (!searchButton) {{
                    console.log('Search button not found, skipping...');
                    return;
                }}

                // Check if search is already enabled
                const isActive = searchButton.getAttribute('aria-pressed') === 'true' || 
                                searchButton.classList.contains('active') || 
                                searchButton.classList.contains('is-active');
                
                if (!isActive) {{
                    console.log('Enabling web search...');
                    searchButton.click();
                    // Wait for search to enable
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    // Verify if search was enabled
                    const isEnabled = document.querySelector('[data-testid*="search-enabled"], .search-enabled');
                    if (isEnabled) {{
                        console.log('Web search enabled successfully');
                    }} else {{
                        console.log('Failed to verify web search status');
                    }}
                }} else {{
                    console.log('Web search is already enabled');
                }}
            }} catch (error) {{
                console.log('Error enabling web search:', error);
            }}
        }}

        // Wait for ChatGPT to finish responding
        function waitForResponseToComplete(timeout = 120000) {{
            return new Promise((resolve) => {{
                console.log('Waiting for response to complete...');
                const startTime = Date.now();
                
                function checkCompletion() {{
                    // Check for stop generating button
                    const stopButton = document.querySelector('button[class*="stop"]');
                    // Check for typing indicator
                    const typingIndicator = document.querySelector('.result-streaming, [class*="typing"], [class*="animate-pulse"]');
                    // Check for send button state
                    const sendButton = document.querySelector('button[data-testid*="send-button"]');
                    
                    const isStillTyping = typingIndicator && 
                                         !typingIndicator.hidden && 
                                         typingIndicator.offsetParent !== null;
                    
                    const isSendButtonDisabled = sendButton && sendButton.disabled;
                    
                    // If stop button is gone, not typing, and send button is enabled
                    const isDone = !stopButton && !isStillTyping && !isSendButtonDisabled;
                    
                    if (isDone || (Date.now() - startTime) > timeout) {{
                        console.log('Response complete or timeout reached');
                        resolve(true);
                    }} else {{
                        setTimeout(checkCompletion, 1000);
                    }}
                }}
                
                checkCompletion();
            }});
        }}

        async function typeText(element, text) {{
            if (!element) return;
            
            // Clear existing text
            element.focus();
            element.textContent = '';
            const inputEvent = new Event('input', {{ bubbles: true, cancelable: true }});
            element.dispatchEvent(inputEvent);
            
            // Type the text
            for (let i = 0; i < text.length; i++) {{
                await new Promise(resolve => setTimeout(resolve, 20 + Math.random() * 30));
                const char = text[i];
                element.textContent += char;
                const inputEvent = new Event('input', {{ bubbles: true, cancelable: true }});
                element.dispatchEvent(inputEvent);
            }}

            //wait function
            function wait(ms) {{
                return new Promise(resolve => setTimeout(resolve, ms));
            }}
        }}        
        async function main() {{
            try {{
                console.log('Starting ChatGPT automation...');
                 
                
                // Wait for chat interface
                await waitForElement('main');


                // Handle cookie consent first
                await handleCookieConsent();

                
                // Enable web search
                await enableWebSearch();

                
                
                // Find the input area
                const textArea = await waitForElement('div[contenteditable="true"], #prompt-textarea, [contenteditable="true"]');
                if (!textArea) throw new Error('Could not find input area');
                
                // Type and submit
                console.log('Typing prompt...');
                await typeText(textArea, `{escaped_prompt}`);
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                // Submit
                const submitButton = await waitForElement('button[data-testid*="send-button"], button[aria-label*="send" i]');
                if (!submitButton || submitButton.disabled) throw new Error('Submit button not available');
                
                console.log('Submitting...');
                submitButton.click();

                
                // Wait for response to complete
                console.log('Waiting for response to finish...');
                await waitForResponseToComplete();
                
                // Additional wait to ensure rendering is complete
                await new Promise(resolve => setTimeout(resolve, 3000));

                // Click sources button to open citations
                const sourcesButton = await waitForElement('button:has(.text-token-text-secondary:contains("Sources"))');
               
                sourcesButton?.click()

                await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for citations to load
                console.log('Chat completed successfully');
                return true;
                
            }} catch (error) {{
                console.error('Error in automation:', error);
                return false;
            }}
        }}

        return main();
    }})()
    """
    
    return script
