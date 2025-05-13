import random
import time
#from win11toast import toast
from seleniumbase import SB
import json
import requests
import os
import sys

try:
    with open("version.txt", "r") as f:
        current_version = f.read().strip()
except FileNotFoundError:
    print("version.txt not found")
    input("Press enter to exit")
    print("Closing...")
    exit(0)
    
cashout_limit = 3 # Minimum scrap for the program to stop betting and cash out
most_money = 0 # The most money the bot has ever had
total_claimed_faucets = 0 # The total amount of claimed faucets
last_rain_check = time.time()

WEBHOOK_URL = "https://discord.com/api/webhooks/1350121755905359983/NcTo1lOPZ7jQDrSl3xVXuUfT9UThxsu9etrO6N0XK6LdNEqdHkVxuvvcJ2ui7kZZkM4k"

def send_discord_message(message):
    data = {
        "content": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    requests.post(WEBHOOK_URL, json=data, headers=headers)


def alert(message):
    #toast("ATTENTION!", message)
    send_discord_message(message)

def version_is_newer(v1, v2): 
    a, b = v1.split('.'), v2.split('.')
    a += ['0'] * (len(b) - len(a))
    b += ['0'] * (len(a) - len(b))
    return list(map(int, a)) > list(map(int, b))

def check_for_updates():
    try:
        REPO_URL = "https://raw.githubusercontent.com/x4ze/banditcampbot/main"
        VERSION_FILE = f"{REPO_URL}/version.txt"
        SCRIPT_FILE = f"{REPO_URL}/main.py"
        print(f"Current script version: {current_version}")
        latest_version = requests.get(VERSION_FILE).text.strip()

        if version_is_newer(latest_version, current_version):
            print(f"A newer version ({latest_version}) is available, downloading...")
            with open(__file__, "w", encoding="utf-8") as f:
                f.write(requests.get(SCRIPT_FILE).text)
            with open("version.txt", "w") as f:
                f.write(latest_version)

            global current_version
            current_version = latest_version
            print(f"Successfully updated to v{current_version}!")
            print("Restarting script...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
            print("Successfully restarted script")
        else:
            print(f"You are using the latest version of the script (v{current_version}).")

    except Exception as e:
        print(f"Failed while checking for updates: {e}")


try:
    check_for_updates()

    with open('users.json') as f:
        data = json.load(f)
        
    accounts_string = ""
    for index, value in enumerate(data):
        accounts_string += f"{value.get('name')}({index}) / "

    
    if len(data) > 1:
        print("Select the index of one of your accounts:")
        try:
            chosen_account = int(input(accounts_string[:-2] + ": "))
        except ValueError:
            print("Invalid input, assuming 0")
            chosen_account = 0
    else:
        chosen_account = 0
    
    jwt_token = data[chosen_account].get('token')
    selected_account = data[chosen_account].get('name')
    shouldCollectRain = data[chosen_account].get('collect_rain') == True
    disableAutoBet = data[chosen_account].get('autobet') == False

    print(f"{"Will" if shouldCollectRain else "Will NOT"} try to collect rain")
    print(f"{"Will NOT" if disableAutoBet else "Will"} use auto bet")
    print("Selected account: " + data[chosen_account].get('name'))

    if "cashout_limit" in data[chosen_account]:
        cashout_limit = data[chosen_account].get('cashout_limit')
        print(f"Cashout limit set to: {cashout_limit}")

    send_discord_message(f"**[{selected_account}]** starting bandit.camp bot **v{current_version}** with a cashout limit of ${cashout_limit}, {"without" if disableAutoBet else "with"} autobet and {"with" if shouldCollectRain else "without"} rain collection")
except FileNotFoundError:
    print("users.json not found, please create a config file")
    input("Press enter to exit")
    print("Closing...")
    exit(0)



print("Starting...")

with SB(uc=True, headless=True) as sb:

    sb.driver.set_window_size(1920, 1080)

    # URL to open
    url = "https://bandit.camp"
    sb.driver.uc_open_with_reconnect(url, 20 + random.uniform(0, 2))

    print("Sleeping for 15 seconds...")
    sb.sleep(15 + random.uniform(0, 1.5))




    
    # Set JWT cookie
    jwt_cookie = {
        "name": "jwt",
        "value": jwt_token,
        "domain": ".bandit.camp",
        "path": "/",
        "httpOnly": True,
        "secure": True
    }
    print("setting jwt cookie")
    sb.driver.add_cookie(jwt_cookie)

    # Refresh the page after setting cookies
    #print("Refreshing website")
    #sb.driver.refresh()
    sb.sleep(3 + random.uniform(0, 2))

    session_data = {
        "banditcamp__settings": '{"value":{"interface":{"chatRight":false,"scrapletNotifs":false,"streamerMode":false,"chat":{"visible":true}},"sounds":{"volumes":{"master":0.7,"game":0.5,"items":0.8,"notifications":0.6}},"games":{"wheel":{"sounds":false,"stacks":[1,10,50,100,500],"simple":true},"coinflip":{"sounds":true},"cases":{"sounds":true,"sorting":"popularity-desc"},"caseBattles":{"sounds":true,"sorting":"popularity-desc","show":10},"caseJackpot":{"sounds":true},"dice":{"sounds":true},"upgrader":{"sounds":true},"mines":{"sounds":true}},"onboarding":{"disabled":false,"seen":[]}},"expire":null}',
    }
    print("setting settings token");
    for key, value in session_data.items():
        sb.driver.execute_script(f"localStorage.setItem('{key}', '{value}');")

    rain_join_button = "#app > div.v-application--wrap > nav > div.v-navigation-drawer__content > div > div.chat-footer.flex-shrink-0 > div.px-4.chat-rain-outer.mb-2 > div > div.v-card__text.px-3.py-3 > button.text-caption.join-btn.font-weight-bold.v-btn.v-btn--has-bg.theme--dark.v-size--default"
    gather_message_el = "#app > div.v-snack.v-snack--active.v-snack--bottom.v-snack--has-background.v-snack--right > div > div.v-snack__content.d-flex.align-center > div > div"
    home_button = "#app > div > header > div > div.v-image.v-responsive.mt-1.mr-5.logo-ctn.flex-grow-0.align-self-start.link.theme--dark > div.v-responsive__content" # used to navigate back home
    wheel_button = "#app > div.v-application--wrap > main > div > div > div > div > div:nth-child(4) > div > a:nth-child(3) > div > div.v-responsive__content"

    print(f"Moving back to the main page from {sb.get_current_url()}")
    sb.driver.uc_open_with_reconnect(url, 20 + random.uniform(0, 2))

    def checkForRain():
        try:
            global last_rain_check
            time_since_last_rain_check = round(time.time() - last_rain_check, 1)
            if time_since_last_rain_check > 120: 
                print("[RAINCHECK] Checking for rain, last check was %ss ago" % time_since_last_rain_check)
            last_rain_check = time.time()
            sb.sleep(0.5 + random.uniform(0, 0.5))
            if sb.driver.is_element_present(rain_join_button):
                    remainingTime = sb.get_text("#app > div > nav > div.v-navigation-drawer__content > div > div.chat-footer.flex-shrink-0 > div.px-4.chat-rain-outer.mb-2 > div > div.v-card__text.px-3.py-3 > h3 > div.countdown.ml-1.text-center.pa-1.rounded.lh-1 > span", timeout=2)
                    rainTip = sb.get_text("#app > div.v-application--wrap > nav > div.v-navigation-drawer__content > div > div.chat-footer.flex-shrink-0 > div.px-4.chat-rain-outer.mb-2 > div > div.v-card__text.px-3.py-3 > p > span > span", timeout=2)
                    rain_participants = sb.get_text("#app > div.v-application--wrap > nav > div.v-navigation-drawer__content > div > div.chat-footer.flex-shrink-0 > div.px-4.chat-rain-outer.mb-2 > div > div.v-card__text.px-3.py-3 > h3 > div.ml-2.text-center.text-caption.rounded.lh-1").strip()
                    print(f"[RAINCHECK] DETECTED A ${rainTip} RAIN with {rain_participants} participants, join up within {remainingTime}!")
                    if shouldCollectRain:
                        try:
                            send_discord_message(f"**[{selected_account}]** DETECTED A **${rainTip} RAIN** with **{rain_participants}** participants, join up within **{remainingTime}**!")
                            if "RAIN JOINED" == sb.get_text("#app > div.v-application--wrap > nav > div.v-navigation-drawer__content > div > div.chat-footer.flex-shrink-0 > div.px-4.chat-rain-outer.mb-2 > div > div.v-card__text.px-3.py-3 > button.text-caption.join-btn.font-weight-bold.v-btn.v-btn--has-bg.theme--dark.v-size--default > span > span", timeout=2).strip():
                                print("Already joined rain, yay!")
                            else:
                                print("Trying to collect rain...")
                                sb.driver.uc_click(rain_join_button, timeout=5)
                                print("Clicked rain join button")
                                sb.wait_for_element_visible(gather_message_el, timeout=16)
                                gather_message = sb.get_text(gather_message_el)
                                print(f"'{gather_message}' received from rain")
                                success_message = "Rakeback Rain"
                                if gather_message == success_message:
                                    print("Successfully joined rain!")
                                    send_discord_message(f"**[{selected_account}]** successfully joined the rain!")
                                sb.driver.save_screenshot("afterRainJoin.png")
                        except Exception as e:
                            if "RAIN JOINED" == sb.get_text("#app > div.v-application--wrap > nav > div.v-navigation-drawer__content > div > div.chat-footer.flex-shrink-0 > div.px-4.chat-rain-outer.mb-2 > div > div.v-card__text.px-3.py-3 > button.text-caption.join-btn.font-weight-bold.v-btn.v-btn--has-bg.theme--dark.v-size--default > span > span", timeout=2).strip():
                                print("Successfully joined rain!")
                                send_discord_message(f"**[{selected_account}]** successfully joined the rain!")
                            else:
                                print(f"Failed to join rain: {e}")
                                sb.driver.save_screenshot("rainError.png")
                                sb.sleep(2)
                                sb.driver.uc_open_with_reconnect(sb.get_current_url(), 10 + random.uniform(0, 2))
                                checkForRain()
        except Exception as e:
            print(f"Failed to join rain: {e}")
            sb.driver.save_screenshot("rainError.png")
            sb.sleep(2)

    def getMoney():
        try:
            global most_money
            money_text = sb.get_text("#app > div > header > div > div.user-container.d-flex.align-center > div.pa-1.wallet-pill.grey900.mr-2.rounded-pill > span > span", timeout=26)
            floatmoney = float(money_text)
            most_money = max(most_money, floatmoney)

            if floatmoney >= cashout_limit and not disableAutoBet:
                print(f"MADE ${floatmoney}, exiting")
                alert(f"**[{selected_account}]** The program has gathered **${floatmoney}** after collecting faucet {total_claimed_faucets} times and is stopping! @here")
                input("Press enter to exit")
                print("Closing...")
                exit(0)

            return floatmoney
        except Exception as e:
            sb.driver.save_screenshot(f"getMoneyError.png")
            isLoggedIn = not sb.driver.is_element_present("#app > div.v-application--wrap > header > div > button")
            if isLoggedIn:
                alert(f"**[{selected_account}]** Failed to log user in, maybe a new token is needed?")
                print(f"Failed to log user in, maybe a new token is needed? {e}")
            else:
                print(f"Failed to get money, likely bandit.camp timeout, wait a few hours {e}")
                alert(f"**[{selected_account}]** Failed while checking money, likely bandit.camp timeout, wait a few hours")
            input("Press enter to exit")
            print("Closing...")
            exit(0)
    
    def collectMoney():
        global total_claimed_faucets
        try:
            sb.sleep(1.5 + random.uniform(0, 0.5))

            money_before = getMoney()
            if (money_before >= 0.03):
                print(f"Has ${money_before}, not clicking button")
                return
            else:
                print(f"Has ${money_before}, will attempt to collect faucet")

            before_clicking_button = time.time()
            sb.driver.uc_click("#app > div > main > div > div > div > div > div.mb-4.col.col-12 > div > div:nth-child(3) > div > div.v-responsive__content > div", timeout=45);
            #print("Clicked first button in %ss" % round(time.time() - before_clicking_button, 1))

            sb.sleep(1.3 + random.uniform(0, 0.5))

            before_clicking_gather_button = time.time()
            sb.driver.uc_click("#app > div.v-dialog__container.v-dialog__container--attached.ready > div > div > div.py-6.px-8.rounded-0.modal-content.v-sheet.theme--dark.grey600 > button", timeout=25)
            print("Clicked gather button in %ss, will wait for loading to finish" % round(time.time() - before_clicking_gather_button, 1))

            
            before_gather_complete = time.time()
            element_loading_icon = "#app > div.v-dialog__container.v-dialog__container--attached.ready > div > div > div.py-6.px-8.rounded-0.modal-content.v-sheet.theme--dark.grey600 > button > span.v-btn__loader"
            sb.wait_for_element_not_visible(element_loading_icon, timeout=80)
            sb.sleep(1.5)

            gather_message = sb.get_text(gather_message_el)
            print(f"'{gather_message}' received after %ss" % round(time.time() - before_gather_complete, 1))
            
            if gather_message == 'You have hit the maximum claimable faucet amount for today.':
                alert(f"**[{selected_account}]** Maximum claimable faucet amount for today reached, bot had ${most_money} at most after {total_claimed_faucets} faucet claims")
                print("Exiting, reached max claimable amount")
                input("Press enter to exit")
                print("Closing...")
                exit(0)
            elif gather_message == 'Your network is rate limited. Disable your VPN or try again later.':
                alert(f"**[{selected_account}]** Network is rate limited, bot had ${most_money} at most after {total_claimed_faucets} faucet claims, stopping program...")
                print("Exiting, network is rate limited")
                input("Press enter to exit")
                print("Closing...")
                exit(0)
            elif gather_message == 'Please try again in a few seconds.':
                print("Sleeping and trying again shortly...")
                overlay = "#app > div.v-overlay.v-overlay--active.theme--dark > div.v-overlay__scrim"
                sb.driver.uc_click(overlay)
                sb.sleep(14 + random.uniform(0, 9))
                #sb.driver.uc_open_with_reconnect(url, 20 + random.uniform(0, 5))
            else: # Successfully collected scrap (probably)
                money_after = getMoney();
                #print(f"Money before: ${money_before}, money after: ${money_after}");
                success = money_after > money_before
                if success:
                    total_claimed_faucets += 1
                    print(f"Collected scrap for the {total_claimed_faucets} time, you now have ${money_after}")
                else:
                    print(f"Failed to collect any scrap for some reason, you still have ${money_after}, reloading page...")
                    sb.driver.uc_open_with_reconnect(url, 16 + random.uniform(0, 1))
                    sb.sleep(20)
            sb.sleep(5 + random.uniform(0, 7))

        except Exception as e:
            sb.driver.save_screenshot(f"error2.png")
            print(f"Failed to find or click the button, reloading page... : {e}")
            sb.driver.uc_open_with_reconnect(url, 16 + random.uniform(0, 1))
            sb.sleep(20)

    def checkForDailyCase():
        dailyCaseAvailable = sb.driver.is_element_present("#app > div.v-application--wrap > main > div > div > div > div > div.mb-4.col.col-12 > div > div:nth-child(2):not(.has-cooldown)")
        if dailyCaseAvailable:
            print("Daily case ready to be opened!")
            openDailyCase()
            checkForRain()
        else:
            remainingTime = sb.get_text("#app > div > main > div > div > div > div > div.mb-4.col.col-12 > div > div:nth-child(2) > div > div.v-responsive__content > div > div > h4 > span")
            print(f"Daily case cooldown, {remainingTime} left")

    def openDailyCase():
        try:
            sb.sleep(1.5 + random.uniform(0, 0.5))

            money_before = getMoney()
            print("[Daily] Opening daily case...")

            before_clicking_button = time.time()
            sb.driver.uc_click("#app > div.v-application--wrap > main > div > div > div > div > div.mb-4.col.col-12 > div > div:nth-child(2):not(.has-cooldown)", timeout=45);
            print("[Daily] Clicked first button in %ss" % round(time.time() - before_clicking_button, 1))

            sb.sleep(1.4 + random.uniform(0, 0.5))

            before_clicking_gather_button = time.time()
            sb.driver.uc_click("#app > div.v-dialog__container.v-dialog__container--attached.ready > div > div > div.py-6.px-8.rounded-0.modal-content.v-sheet.theme--dark.grey700 > div > div > div.overlay > div > button", timeout=25)
            print("[Daily] Clicked open button in %ss" % round(time.time() - before_clicking_gather_button, 1))
            sb.sleep(2)
            print("[Daily] Opening case...")

            before_gather_complete = time.time()
            sb.wait_for_element_visible(gather_message_el, timeout=80)

            #sb.sleep(30)
            sb.sleep(1.5)

            gather_message = sb.get_text(gather_message_el)
            print(f"[Daily] message '{gather_message}' received after %ss" % round(time.time() - before_gather_complete, 1))

            #close the daily case window
            overlay = "#app > div.v-overlay.v-overlay--active.theme--dark > div.v-overlay__scrim"
            sb.driver.uc_click(overlay)

            money_after = getMoney();
            success = money_after > money_before
            if success:
                print(f"[Daily] Daily case opened, you now have ${money_after}")
            else:
                print(f"Probably failed to open case, you still have ${money_after}, reloading page...")
                sb.driver.uc_open_with_reconnect(url, 16 + random.uniform(0, 1))
                sb.sleep(20)
            sb.sleep(5 + random.uniform(0, 7))

        except Exception as e:
            sb.driver.save_screenshot(f"error1.png")
            print(f"Failed to find or click the button: {e}")
            sb.driver.uc_open_with_reconnect(url, 16 + random.uniform(0, 1))
            sb.sleep(20)


    def betOnWheel():
        try:
            # Navigate to the wheel page
            sb.driver.uc_click(wheel_button, timeout=20)

            # Wait for the lock icon to disappear
            #print("Navigated to /wheel & waiting for wheel to be ready...")

            def place_money():

                checkForRain()

                lock_icon = "#app > div > main > div > div > div.container.game-container > div > div:nth-child(2) > div > div.bet-interface-blocks.mb-3 > div.flex-grow-1 > div.row.mb-3.timer-row.row--dense > div.py-0.col.col-4 > div > svg > g"
                bet_input = "#app > div > main > div > div > div.container.game-container > div > div:nth-child(2) > div > div.bet-interface-blocks.mb-3 > div.flex-grow-1 > div.bg-ui-panel.px-4.py-3.mb-2 > div.simple-bet-input > div > div > div > div > div > input"
                money_before = getMoney();
                bet_amount = money_before;

                if bet_amount <= 0:
                    print("No money to bet, exiting...")
                    return
                
                sb.sleep(1.5 + random.uniform(0, 1))
                sb.type(bet_input, bet_amount)
                sb.wait_for_element_not_visible(lock_icon, timeout=35)

                #print("Wheel is open for bets!")

                
                

                sb.sleep(0.2 + random.uniform(0, 1))
                bet_1_button = "#app > div.v-application--wrap > main > div > div > div.container.game-container > div > div:nth-child(2) > div > div.bet-interface-blocks.mb-3 > div.flex-grow-1 > div.bg-ui-panel.bet-fields.py-2.px-3.mb-3 > div > div:nth-child(1) > div > div.v-responsive__content > div.pa-1.scrap-ctn"
                bet_3_button = "#app > div.v-application--wrap > main > div > div > div.container.game-container > div > div:nth-child(2) > div > div.bet-interface-blocks.mb-3 > div.flex-grow-1 > div.bg-ui-panel.bet-fields.py-2.px-3.mb-3 > div > div:nth-child(2) > div > div.v-responsive__content > div.pa-1.scrap-ctn"
                bet_5_button = "#app > div.v-application--wrap > main > div > div > div.container.game-container > div > div:nth-child(2) > div > div.bet-interface-blocks.mb-3 > div.flex-grow-1 > div.bg-ui-panel.bet-fields.py-2.px-3.mb-3 > div > div:nth-child(3) > div > div.v-responsive__content > div.pa-1.scrap-ctn"
                bets = [bet_1_button, bet_1_button, bet_1_button, bet_3_button, bet_3_button, bet_5_button]
                randNumber = random.randint(0, len(bets) - 1 - (1 if money_before >= 1.5 else 0)) # exclude bets for 5 if money is more than 1.5
                bet = bets[randNumber]

                bet_name = {
                    bet_1_button: "1",
                    bet_3_button: "3",
                    bet_5_button: "5"
                }.get(bet, "unknown")

                print(f"Betting ${money_before} on {bet_name} on the wheel")

                sb.driver.uc_click(bet, timeout=40)
                sb.wait_for_element_visible(lock_icon, timeout=60)
                #print("Wheel started spinning...")
                sb.wait_for_element_not_visible(lock_icon, timeout=35)
                sb.sleep(1 + random.uniform(0, 0.5))
                money_after = getMoney()
                success = money_after > money_before

                if success:
                    print(f"The wheel landed on {bet_name}, you now have ${money_after}, waiting for next...")
                    sb.sleep(1.5 + random.uniform(0, 2))
                    place_money()
                elif money_after == money_before:
                    print(f"You still have ${money_before}, bet likely failed, retrying...")
                    sb.sleep(1.5 + random.uniform(0, 2))
                    place_money()
                else:
                    last_spin_result = "#app > div.v-application--wrap > main > div > div > div.container.game-container > div > div:nth-child(2) > div > div.bet-interface-blocks.mb-3 > div.round-history.ml-3 > div > svg:nth-child(3)"
                    wheel_result = sb.driver.execute_script("return [...document.querySelector(arguments[0]).classList].find((i) => i.includes('field-icon-')).split('-')[2]", last_spin_result)
                    print(f"NOOO! Wheel landed on {wheel_result}, not {bet_name}, you lost ${money_before}. The most money you've had today is ${most_money}")

            place_money()
            # Navigate back to the main page
            #sb.uc_open_with_reconnect(url, 15 + random.uniform(0, 1))
            
            sb.driver.uc_click(home_button, timeout=20)
            #print("Navigated back to the main page")



        except Exception as e:
            print(f"Failed to bet on wheel: {e}")
            sb.driver.save_screenshot("betOnWheelError.png")
            sb.sleep(2)
            sb.driver.uc_open_with_reconnect(url, 20 + random.uniform(0, 2))
            sb.sleep(10 + random.uniform(0, 1.5))

    sb.sleep(10)

    while True:
        try:
            money = getMoney()
            if float(money) > 0: print(f"Current money: ${money}")
            checkForRain()
            if disableAutoBet:
                checkForDailyCase()
            elif money < 0.03:
                faucetAvailable = sb.driver.is_element_present("#app > div.v-application--wrap > main > div > div > div > div > div.mb-4.col.col-12 > div > div:nth-child(3):not(.has-cooldown)")
                if faucetAvailable: # if scrap gather is not on cooldown
                    collectMoney()
                    checkForRain()
                    checkForDailyCase()
                else:
                    remainingTime = sb.get_text("#app > div > main > div > div > div > div > div.mb-4.col.col-12 > div > div:nth-child(3) > div > div.v-responsive__content > div > div > h4 > span")
                    print(f"Faucet collection is on cooldown, {remainingTime} left")
            else:
                betOnWheel()

            sleeptime = 49 + random.uniform(0, 30)
            #print(f"Action finished, sleeping for {round(sleeptime)} seconds")
            sb.sleep(sleeptime)
        except Exception as e:
            print(f"ATTENTION! AN UNKNOWN ERROR OCCURED, a screenshot has been saved, error: {e}")
            sb.driver.save_screenshot("UNKNOWNERROR.png")
            sb.sleep(2 + random.uniform(0, 5))
            sb.driver.uc_open_with_reconnect(url, 20 + random.uniform(0, 2))
            sb.sleep(10 + random.uniform(0, 1.5))