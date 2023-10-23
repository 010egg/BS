import random
import collections
from enum import Enum, unique

class Card:
    # 字典定义了扑克牌的数值与其对应的字符表示
    values = {
        2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
        8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'
    }

    # 字典定义了花色与其对应的特殊字符
    suits = {'hearts': '♥', 'diamonds': '♦', 'clubs': '♣', 'spades': '♠'}

    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        # 这会返回例如 '♠A' 这样的字符串，用图案和值表示卡片
        return f'{self.suits[self.suit]}{self.values[self.value]}'


class Player:
    def __init__(self, name, chips, is_human=True):
        self.name = name
        self.hand = []
        self.chips = chips
        self.current_bet = 0
        self.folded = False
        self.is_human = is_human  # 新增字段，判断是否是人类玩家

    # decide_action方法现在会根据玩家类型（人类或电脑）来决定如何选择行动
    def get_player_action():
        # 定义有效的动作
        valid_actions = ["跟一手", "加注", "弃牌"]

        while True:  # 保持循环直到得到有效输入
            # 提示用户输入
            action = input("请选择您的操作 (跟一手, 加注, 弃牌): ").strip()

            # 如果输入是有效的，就退出循环
            if action in valid_actions:
                return action  # 返回有效的动作

            # 如果输入无效，提示用户重新输入
            else:
                print("无效的操作。请重新输入，只能选择 '跟一手', '加注', 或 '弃牌'。")
    def decide_action(self, min_bet):
        if self.folded:
            return '弃牌', 0

        if self.is_human:  # 如果是人类玩家
            valid_actions = ["跟一手", "加注", "弃牌"]
            while True:  # 保持循环直到得到有效输入
                action = input(f"{self.name} - chips: {self.chips}, current bet: {self.current_bet}, min bet: {min_bet} (跟一手, 加注, 弃牌): ")
                if action in valid_actions:
                    break
                else:
                    print("无效的操作。请重新输入，只能选择 '跟一手', '加注', 或 '弃牌'。")
            if action == '加注':
                amount = int(input("加注 amount: "))
                if amount <= self.chips and amount >= min_bet:
                    return '加注', amount
                else:
                    print("Invalid amount. Please 加注 within your chip limit and at least to the minimum bet.")
                    return self.decide_action(min_bet)
            elif action == '跟一手':
                return '跟一手', min_bet - self.current_bet  # Only need to supplement to reach min_bet
            else:  # action == '弃牌'
                return '弃牌', 0
        else:  # 如果是电脑玩家
            actions = ['跟一手', '加注', '弃牌']
            action = random.choice(actions)  # 随机选择行动
            amount = 0
            if action == '加注':
                # 如果动作是加注，金额在最小赌注和玩家剩余筹码之间随机选择
                amount = random.randint(min_bet, self.chips)

            elif action == '跟一手':
                # 如果动作是跟注，金额是最小赌注减去玩家当前的赌注
                # 确保玩家至少投入等于当前轮最小赌注的筹码
                amount = min_bet - self.current_bet
            print(f"Computer player {self.name} decides to {action}" + (f" with an amount of {amount}" if action == '加注' else ""))
            return action, amount

    def adjust_chips(self, amount):
        # 确保此方法返回调整的筹码数量
        self.chips -= amount
        self.current_bet += amount
        print(self.chips)
        return amount
def replace_t_with_10(cards):
    return [card.replace('T', '10') if 'T' in card else card for card in cards]

class PokerGame:
    def __init__(self, starting_chips):
        self.deck = [f"{r}{s}" for r in "23456789TJQKA" for s in Card.suits.values()]  # T is for Ten
        # self.players = [Player(starting_chips) for _ in range(4)]
        self.community_cards = []
        self.pot = 0
        self.remain_players = []
        self.players = [
            Player("You", starting_chips, is_human=True),  # 人类玩家
            Player("AI 唐龙", starting_chips, is_human=False),  # 电脑玩家
            Player("AI 张涛", starting_chips, is_human=False),  # 电脑玩家
            Player("AI 刚子", starting_chips, is_human=False),  # 电脑玩家
        ]

    def active_players(self):
        """返回还未弃牌的玩家数量"""
        return len([player for player in self.players if not player.folded])
    def play(self):
        print("Game starts!")
        self.deck = random.sample(self.deck, len(self.deck))  # Shuffling the deck

        # Initial blind betting
        small_blind = 5
        big_blind = 10
        print(F"Small blind{self.players[0].name}的余额:")
        self.pot += self.players[0].adjust_chips(small_blind)  # Small blind
        print(f"Big blind{self.players[1].name}的余额:")
        self.pot += self.players[1].adjust_chips(big_blind)  # Big blind

        print(f"Current pot: {self.pot}")  # 打印当前底池金额


        # Deal initial cards
        for player in self.players:
            player.hand = [self.deck.pop(), self.deck.pop()]
            if player.is_human:
                player.hand = replace_t_with_10(player.hand)
                print(f"{player.name}, your hand: {player.hand}")
            else:
                print(f"{player.name}'s hand has been dealt.")  # 对于AI玩家，我们不显示他们的手牌


        self.betting_round()
        # Initial betting round
        if self.active_players() == 1:
            self.showdown()
            return  # 结束游戏
        if not all(player.folded for player in self.players):
            # Flop
            self.community_cards.extend([self.deck.pop() for _ in range(3)])
            self.community_cards = replace_t_with_10(self.community_cards)
            self.players[0].hand = replace_t_with_10(self.players[0].hand)
            print(f"{self.players[0].name}, your hand: {self.players[0].hand}")
            print(f"Community cards: {self.community_cards}")
            print(f"Current pot: {self.pot}")  # 打印当前底池金额
            for player in self.players:
                player.current_bet = 0
            self.betting_round()
            if self.active_players() == 1:
                self.showdown()
                return  # 结束游戏


        if not all(player.folded for player in self.players):
            # Turn
            self.community_cards.append(self.deck.pop())
            self.players[0].hand = replace_t_with_10(self.players[0].hand)
            self.community_cards = replace_t_with_10(self.community_cards)
            print(f"{self.players[0].name}, your hand: {self.players[0].hand}")
            print(f"Community cards: {self.community_cards}")
            print(f"Current pot: {self.pot}")  # 打印当前底池金额
            for player in self.players:
                player.current_bet = 0
            self.betting_round()
            if self.active_players() == 1:
                self.showdown()
                return  # 结束游戏


        if not all(player.folded for player in self.players):
            # River
            self.community_cards.append(self.deck.pop())
            self.players[0].hand = replace_t_with_10(self.players[0].hand)
            self.community_cards = replace_t_with_10(self.community_cards)
            print(f"{self.players[0].name}, your hand: {self.players[0].hand}")
            print(f"Community cards: {self.community_cards}")
            print(f"Current pot: {self.pot}")  # 打印当前底池金额
            for player in self.players:
                player.current_bet = 0
            if self.active_players() == 1:
                self.showdown()
                return  # 结束游戏






        self.showdown()


    def betting_round(self):
        highest_bet = max(player.current_bet for player in self.players)
        print(highest_bet)
        for player in self.players:
            if player.folded:
                continue

            action, amount = player.decide_action(highest_bet)
            if action == '弃牌':
                player.folded = True
            else:
                print(f"{player.name} 的余额")
                player.adjust_chips(amount)

                self.pot += amount
                if action == '加注':
                    highest_bet = player.current_bet
        for player in self.players:
            if player.folded or player.current_bet == highest_bet:
                continue  # 如果玩家已经弃牌或已经达到最高下注，则无需采取行动

            # 询问玩家是想要补足差额还是弃牌
            print(f"Minimum 跟一手 amount is {highest_bet}. You have already bet {player.current_bet}.")
            valid_actions2 = ["跟一手", "弃牌"]
            while True:  # 保持循环直到得到有效输入
                action = input(f"Do you want to '跟一手' to match the highest bet or '弃牌'? ").lower()
                if action in valid_actions2:
                    break
                else:
                    print("无效的操作。请重新输入，只能选择 '跟一手', 或 '弃牌'。")
            if action == '跟一手':
                additional_bet = highest_bet - player.current_bet
                player.adjust_chips(additional_bet)
                self.pot += additional_bet
            else:
                player.folded = True  # 玩家选择弃牌




    def showdown(self):
        remaining_players = [player for player in self.players if not player.folded]
        if len(remaining_players) == 1:
            print(f"Winner by 弃牌: {remaining_players[0].name}!")
        else:
            # 这个示例不会实际比较手牌，因为这需要一个手牌评估器。
            # 取而代之，我们只是宣布有一场摊牌，并展示玩家的手牌。
            print("Showdown! Players reveal their cards:")
            for player in remaining_players:
                print(f"{player.name}: {player.hand}")
            self.remain_players = [
                {'name': player.name, 'hand': player.hand} for player in remaining_players
            ]
        # The pot would be awarded based on hand comparison or split in case of a tie.
        # For simplicity, we'll just split the pot among remaining players.
        for player in remaining_players:
            player.chips += self.pot // len(remaining_players)
          # Resetting the pot for the next game
        return


# 定义手牌的等级
class HandRanking(Enum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

    def __lt__(self, other):
        return self.value < other.value


def evaluate_hand(hand):
    # 首先，我们需要转换卡牌的表示方法并提取基本信息
    values_str = '2345678910JQKA'  # 已更新，用'10'代替'T'
    suits = [card[-1] for card in hand]  # 提取花色

    # 提取数值并转换为整数
    values = []
    for card in hand:
        value_str = card[:-1]  # 由于'10'有两个字符，我们不能只简单地去掉最后一个字符来提取数值
        if value_str == "10":
            values.append(10)
        elif value_str == 'A':
            values.append(14)
        elif value_str == 'K':
            values.append(13)
        elif value_str == 'Q':
            values.append(12)
        elif value_str == 'J':
            values.append(11)
        else:
            values.append(values_str.index(value_str) + 2)  # 因为我们的索引是从'2'开始的
        # print(value_str)
    value_counts = collections.Counter(values)
    print(value_counts)
    suit_counts = collections.Counter(suits)
    print(suit_counts)

    # 计算各种数值和花色的数量
    count_values = {value: values.count(value) for value in set(values)}
    count_suits = {suit: suits.count(suit) for suit in set(suits)}

    # 检查是否为同花顺
    is_flush = max(count_suits.values()) == 5
    sorted_values = sorted(values)
    is_straight = False
    if len(set(values)) == 5:
        if max(values) - min(values) == 4:
            is_straight = True
        # 特殊情况，如果是 A-2-3-4-5 的顺子
        elif set(values) == {14, 2, 3, 4, 5}:
            is_straight = True
            values = {1, 2, 3, 4, 5}
        # 特殊情况，最高顺子 10-J-Q-K-A
        elif set(values) == {14, 13, 12, 10, 11}:
            is_straight = True
              # 在这种情况下，Ace 作为最高牌 (表示为 14)

    if is_flush and is_straight:
        return (HandRanking.STRAIGHT_FLUSH, [max(sorted_values)])  # 使用 sorted_values 获取正确的最高牌

    # 检查四条
    if 4 in count_values.values():
        card_val = [val for val, count in count_values.items() if count == 4][0]
        return (HandRanking.FOUR_OF_A_KIND, [card_val])

    # 检查满堂红（三带二）
    if 3 in count_values.values() and 2 in count_values.values():
        three_val = [val for val, count in count_values.items() if count == 3][0]
        two_val = [val for val, count in count_values.items() if count == 2][0]
        return (HandRanking.FULL_HOUSE, [three_val, two_val])

    # 检查同花
    if is_flush:
        return (HandRanking.FLUSH, sorted(values, reverse=True))  # 需要所有的牌值来比较

    # 检查顺子
    if is_straight:
        return (HandRanking.STRAIGHT, [max(values)])

    # 检查三条
    # 检查三条
    if 3 in count_values.values():
        # 找出是哪个数值的三条
        three_val = [val for val, count in count_values.items() if count == 3][0]
        # 从手中的牌中移除三条，这样我们就可以比较剩下的牌
        remaining_cards = sorted([val for val in values if val != three_val], reverse=True)
        # 返回三条的数值，加上剩余牌的数值，以便在必要时进行进一步比较
        return (HandRanking.THREE_OF_A_KIND, [three_val] + remaining_cards)

    # 检查两对
    pairs = [val for val, count in count_values.items() if count == 2]
    # 检查两对
    if len(pairs) == 2:
        # 排序，以便首先比较较大的对子
        sorted_pairs = sorted(pairs, reverse=True)
        # 找出不在对子中的单张牌的值
        single_val = [val for val in values if val not in pairs][0]
        # 返回值应该首先包括对子（从大到小），然后是单张牌的值
        return (HandRanking.TWO_PAIR, sorted_pairs + [single_val])

    # 检查一对
    # 检查一对
    if len(pairs) == 1:
        # 找出对子的值
        pair_val = pairs[0]
        # 找出不在对子中的牌，它们需要被用于进一步的比较
        high_cards = sorted([val for val in values if val not in pairs], reverse=True)
        # 返回值应该首先是对子的值，然后是剩余牌的值（从大到小）
        return (HandRanking.ONE_PAIR, [pair_val] + high_cards)

    # 如果都不是，则返回高牌
    return (HandRanking.HIGH_CARD, sorted(values, reverse=True))



def compare_cards(card_values1, card_values2):
    # 这个函数接受两手牌的数值列表，并逐一进行比较
    for v1, v2 in zip(card_values1, card_values2):
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
    return 0  # 如果所有数值都相等，则返回0表示平局

def compare_hands(final_hands):
    hands = [hand for name, hand in final_hands]
    evaluated_hands = [(i, evaluate_hand(hand)) for i, hand in enumerate(hands)]
    print(evaluated_hands, "--")
    # 找出最好的牌型等级
    best_hand_rank = max(evaluated_hands, key=lambda x: x[1][0])[1][0]

    # 筛选出具有最佳牌型等级的手牌
    hands_with_best_rank = [hand for hand in evaluated_hands if hand[1][0] == best_hand_rank]

    if len(hands_with_best_rank) == 1:
        return [hands_with_best_rank[0][0]]  # 返回赢家的索引

    # 对于具有相同最佳牌型的手牌，进行更细致的比较
    best_hands = []
    best_cards = None
    for hand in hands_with_best_rank:
        if best_cards is None or compare_cards(hand[1][1], best_cards) > 0:
            best_hands = [hand]  # 这是目前最好的手牌
            best_cards = hand[1][1]  # 保持当前最好的牌面数值
        elif compare_cards(hand[1][1], best_cards) == 0:
            best_hands.append(hand)  # 如果一样好，加入到最好的手牌列表中

    return [hand[0] for hand in best_hands]  # 返回所有赢家的索引

def final_showdown(players, community_cards):
    final_hands = []

    for player in players:
        valid_hand = False
        while not valid_hand:
            print(f"Player {player['name']}, your hand is: {player['hand']}")
            print(f"Community cards are: {community_cards}")
            valid_hand_card = ["no", '1', '2']
            unique_discard_input = []  # 用于存储去重后的输入

            while True:  # 保持循环直到得到有效输入
                # 获取要丢弃的牌的索引
                discard_input = input(
                    "Enter the indices (1-based) of cards you wish to discard (space-separated, or 'no'): ")

                # 分割输入的字符串，并去除多余空格
                split_input = discard_input.strip().split()

                # 验证输入是否都在允许的列表里，且没有重复项
                if all(choice in valid_hand_card for choice in split_input) and len(split_input) == len(
                        set(split_input)):
                    # 如果输入的是'no'，我们确认列表里只有一个元素
                    if 'no' in split_input and len(split_input) == 1:
                        break  # 如果是'no'，则退出循环
                    # 现在我们检查是否所有输入的索引都是有效的，且没有'no'
                    elif 'no' not in split_input and all(num in ['1', '2'] for num in split_input):
                        unique_discard_input = split_input  # 保存去重后的输入
                        break  # 如果输入有效，则退出循环
                # 如果验证失败，提示错误信息
                print("无效的操作。请重新输入，只能选择丢弃手牌 '1', '2', 或 'no'。请不要输入重复项或与'no'混合。")

            # 接下来，您可以用unique_discard_input里的值继续进行其他逻辑处理。

            try:
                if discard_input.lower() != 'no':
                    discard_indices = [int(x) - 1 for x in discard_input.split()]  # 减 1 转换为内部索引
                else:
                    discard_indices = []

                # 检查索引有效性
                if any(index < 0 or index >= len(player['hand']) for index in discard_indices):
                    print("Invalid index detected. Please input indices in the correct range.")
                    continue  # 如果有无效的索引，重新开始循环
                valid_indices = set(range(1, 6))  # 合法的输入范围
                while True:
                    # 提示用户输入，并用空格分割
                    input_str = input(
                        "Enter the indices (1-based) of community cards you wish to use at least 3 (space-separated): ")
                    input_numbers = input_str.split()

                    # 尝试将输入转换为整数集合（自动去重）
                    try:
                        selected_indices = set(int(num) for num in input_numbers)
                    except ValueError:
                        # 如果输入不是数字，打印错误信息并继续循环
                        print("无效的输入。确保您输入的是数字。")
                        continue

                    # 检查所选索引是否有效，并且至少选择了3个不同的索引
                    if selected_indices.issubset(valid_indices) and len(selected_indices) >= 3:
                        community_input = list(selected_indices)  # 如果有效，返回选择的数字列表
                        break  # 验证通过，跳出循环
                    else:
                        print("无效的操作。请至少选择3个不同的数字，每个数字必须在1到5之间。")

                community_indices = [int(x) - 1 for x in community_input]  # 减 1 转换为内部索引

                # 检查索引有效性
                if any(index < 0 or index >= len(community_cards) for index in community_indices):
                    print("Invalid index detected. Please input indices in the correct range.")
                    continue  # 如果有无效的索引，重新开始循环

                # 构建最终的手牌
                final_hand = [card for i, card in enumerate(player['hand']) if i not in discard_indices]
                final_hand.extend(community_cards[i] for i in community_indices)

                if len(final_hand) == 5:
                    valid_hand = True
                    final_hands.append((player['name'], final_hand))  # 存储玩家的名字和最终的手牌
                else:
                    print("Error: Your final hand does not have exactly 5 cards. Please choose again.")

            except ValueError:
                # 捕获到非整数输入，提示错误并重新开始循环
                print("Invalid input detected. Please ensure you enter valid numbers.")

    # 显示玩家的最终手牌
    for name, hand in final_hands:
        print(f"Player {name}, your final hand is: {hand}")

    return final_hands  # 返回最终手牌列表以用于进一步的比较或处理


# 假设的玩家数据和公共牌
# players = [
#     {'name': 'Player1', 'hand': ['2♦', '3♠']},
#     {'name': 'Player2', 'hand': ['K♦', 'A♦']},
# ]
# community_cards = ['10♠', 'J♦', 'Q♠', 'K♠', 'A♠']

# 运行最终对决过程

# 在这一点上，您将拥有每个玩家最终的手牌，然后可以继续评估这些手牌来确定胜者。

# winning_players 包含了获胜玩家的索引列表

# Starting the game
game = PokerGame(starting_chips=1000)
game.play()
final_hands = final_showdown(game.remain_players, game.community_cards)
#选择底牌（3-5张），之后得到最终的手牌作为评估器的输入
#评估胜利者，并瓜分奖池
if len(final_hands) == 1:
    print(f"Winner by 弃牌: {final_hands[0].name}!")
else:
    winning_players = compare_hands(final_hands)
    for i in winning_players:
        print(final_hands[i])
print(game.pot)
game.pot = 0