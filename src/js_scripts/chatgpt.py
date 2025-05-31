def get_chatgpt_scripts(prompt):
    # Properly escape the prompt for JavaScript
    escaped_prompt = prompt.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$').replace('\n', '\\n')
    
    # Using triple quotes for the multi-line string with raw string prefix
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
        }}        

        // Function to wait for a specific time
        function wait(ms) {{
            return new Promise(resolve => setTimeout(resolve, ms));
        }}

        // Function to check if sources panel is visible
        function checkIfSourcesPanelVisible() {{
            const sourcesPanel = document.querySelector('[data-testid*="sources-panel"], [class*="sources-panel"], [class*="citation-panel"]');
            return sourcesPanel && sourcesPanel.offsetParent !== null;
        }}

        // Improved function to click the sources button
        async function clickSourcesButton() {{
            try {{
                console.log('Starting enhanced sources button detection...');
                
                // Wait a bit for any animations to complete
                await wait(2000);
                
                // Function to try multiple click methods on an element
                const tryClick = async (element) => {{
                    const clickMethods = [
                        () => element.click(),
                        () => {{
                            const rect = element.getBoundingClientRect();
                            const x = rect.left + rect.width / 2;
                            const y = rect.top + rect.height / 2;
                            
                            // Try dispatching mouse events
                            ['mousedown', 'mouseup', 'click'].forEach(eventType => {{
                                const event = new MouseEvent(eventType, {{
                                    view: window,
                                    bubbles: true,
                                    cancelable: true,
                                    clientX: x,
                                    clientY: y
                                }});
                                element.dispatchEvent(event);
                            }});
                        }},
                        () => {{
                            // Try dispatching pointer events
                            ['pointerdown', 'pointerup'].forEach(eventType => {{
                                const event = new PointerEvent(eventType, {{
                                    view: window,
                                    bubbles: true,
                                    cancelable: true
                                }});
                                element.dispatchEvent(event);
                            }});
                        }}
                    ];
                    
                    for (const method of clickMethods) {{
                        try {{
                            method();
                            await wait(1000);
                            
                            // Check if sources panel is now visible
                            if (checkIfSourcesPanelVisible()) {{
                                console.log('Sources panel appeared after click attempt');
                                return true;
                            }}
                        }} catch (e) {{
                            console.log('Click method failed:', e);
                        }}
                    }}
                    
                    return false;
                }};
                
                // Function to find potential sources buttons
                const findPotentialButtons = () => {{
                    // Try multiple selectors
                    const selectors = [
                        // Common button selectors
                        'button[class*="source"]',
                        'button[class*="footnote"]',
                        'button[aria-label*="source"]',
                        'button[aria-label*="citation"]',
                        'button[data-testid*="source"]',
                        'div[role="button"][class*="source"]',
                        
                        // Look for elements with source/citation text
                        'button:has(> div:contains("Sources"))',
                        'button:has(> span:contains("Sources"))',
                        'button:has(> div > span:contains("Sources"))',
                        'button:has(svg + div:contains("Sources"))',
                        
                        // Look for elements with favicon images
                        'button:has(img[src*="favicon"])',
                        'div[class*="source"] button',
                        
                        // Look for elements with specific data attributes
                        '[data-testid*="source"]',
                        '[data-testid*="citation"]',
                        '[data-testid*="footnote"]'
                    ];
                    
                    const buttons = [];
                    
                    // Try each selector
                    for (const selector of selectors) {{
                        try {{
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {{
                                if (el.offsetParent !== null && 
                                    window.getComputedStyle(el).display !== 'none' &&
                                    !buttons.includes(el)) {{
                                    buttons.push(el);
                                }}
                            }}
                        }} catch (e) {{
                            console.log(`Error with selector ${{selector}}:`, e);
                        }}
                    }}
                    
                    return buttons;
                }};
                
                // Find all potential buttons
                const potentialButtons = findPotentialButtons();
                console.log(`Found ${{potentialButtons.length}} potential buttons to try`);
                
                // Try each button
                for (const button of potentialButtons) {{
                    console.log('Trying button:', button);
                    const success = await tryClick(button);
                    if (success) {{
                        console.log('Successfully clicked sources button');
                        return true;
                    }}
                }}
                
                // If we get here, try one more approach - look for any clickable elements near "Sources" text
                console.log('Trying text-based approach...');
                const textNodes = document.evaluate(
                    "//*[contains(translate(., 'SOURCES', 'sources'), 'sources') or contains(., 'Citations')]",
                    document,
                    null,
                    XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                    null
                );
                
                for (let i = 0; i < textNodes.snapshotLength; i++) {{
                    const node = textNodes.snapshotItem(i);
                    console.log('Found text node:', node.textContent.trim());
                    
                    // Find the nearest clickable parent
                    let element = node;
                    let levels = 0;
                    while (element && levels < 5) {{
                        if (element.tagName === 'BUTTON' || 
                            element.getAttribute('role') === 'button' ||
                            element.onclick ||
                            element.getAttribute('onclick') ||
                            element.classList.contains('group') ||
                            element.getAttribute('class')?.includes('source') ||
                            element.getAttribute('class')?.includes('footnote')) {{
                            
                            console.log('Found potential clickable parent:', element);
                            const success = await tryClick(element);
                            if (success) return true;
                            break;
                        }}
                        element = element.parentElement;
                        levels++;
                    }}
                }}
                
                console.log('Failed to find and click sources button after all attempts');
                return false;
                
            }} catch (error) {{
                console.error('Error in clickSourcesButton:', error);
                return false;
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
                await wait(2000);
                
                // Submit
                const submitButton = await waitForElement('button[data-testid*="send-button"], button[aria-label*="send" i]');
                if (!submitButton || submitButton.disabled) throw new Error('Submit button not available');
                
                console.log('Submitting...');
                submitButton.click();

                // Wait for response to complete with improved detection
                console.log('Waiting for response to finish...');
                await waitForResponseToComplete();
                
                // Additional wait to ensure rendering is complete
                await wait(2000);

                // Try to click sources button with revamped function
                console.log('Attempting to click sources button...');
                const sourcesClicked = await clickSourcesButton();
                
                if (sourcesClicked) {{
                    console.log('Successfully opened sources panel');
                    await wait(5000); // Wait for sources to fully load
                }} else {{
                    console.log('Failed to open sources panel after all attempts');
                }}

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
