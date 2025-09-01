import os
import arcade
from arcade import gui

LETTERS = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c',
           'v', 'b', 'n', 'm']

# Pile constants, to track in what pile LetterCards are
PILE_COUNT = 5
PILE_ONE = 0
PILE_TWO = 1
PILE_THREE = 2
PILE_FOUR = 3
PILE_FIVE = 4


class LetterCard(arcade.Sprite):

    def __init__(self, nr):
        super().__init__(hit_box_algorithm='None', scale=0.9)
        self.nr = nr
        
        # In arcade 3.x, load_spritesheet returns a SpriteSheet object
        spritesheet_path = os.path.join('assets', 'spritesheet.png')
        spritesheet = arcade.load_spritesheet(spritesheet_path)
        
        # Get textures using the correct API
        # Based on 1280x384 image and 104 total sprites (26 letters × 4 states each)
        try:
            self.textures = spritesheet.get_texture_grid(
                size=(64, 64),     # sprite width, height (1280/20=64, 384/6=64)
                columns=20,        # 
                count=104          # total number of sprites
            )
        except Exception as e:
            # Fallback: load single texture
            print(f"Warning: Could not load spritesheet grid: {e}")
            base_texture = arcade.load_texture(spritesheet_path)
            self.textures = [base_texture] * 104

        self.letter = LETTERS[int(self.nr / 4)]
        if self.nr < len(self.textures):
            self.texture = self.textures[nr]
        else:
            # Fallback texture
            self.texture = arcade.load_texture(spritesheet_path)
        self.zero_or_one = False

        self.og_position = None
        self.what_color_is_this = None

        self.mat_index = None
        self.is_duplicate = False

    def white(self):
        self.set_texture(self.nr)

    def black_or_white(self):
        self.zero_or_one = not self.zero_or_one
        self.set_texture(self.nr + int(self.zero_or_one))

    def green(self):
        self.set_texture(self.nr + 2)
        self.what_color_is_this = 'green'

    def yellow(self):
        self.set_texture(self.nr + 3)
        self.what_color_is_this = 'yellow'


class MyGame(arcade.Window):
    """Main application class"""

    def __init__(self):
        super().__init__(700, 500, 'wordle assistant')

        arcade.set_background_color(arcade.color.ANTI_FLASH_WHITE)

        self.letter_card_list = None

        self.held_letter_cards = None

        # Original location of selected card in case they need to return
        self.held_letter_cards_original_position = None

        # Sprite list with all the mats that cards lay on.
        self.pile_mat_list = None

        self.piles = None

        self.manager = gui.UIManager()
        self.manager.enable()

        # Green or yellow switch
        self.green_or_yellow = False
        self.green_yellow = gui.UITextureButton(texture=arcade.load_texture(os.path.join('assets', f"{int(self.green_or_yellow)}.png")), scale=0.6, x=333, y=300)

        # Clear button
        self.clear_button = gui.UIFlatButton(text='Clear', x=70, y=72, width=58, height=48)

        # Forward button
        self.forward_button = gui.UITextureButton(texture=arcade.load_texture(
            ':resources:/onscreen_controls/flat_dark/play.png'), x=585, y=72,
            texture_hovered=arcade.load_texture(':resources:/onscreen_controls/shaded_dark/play.png'))

    def setup(self):
        """Game setup. Call to restart/clear"""
        self.letter_card_list = arcade.SpriteList()
        # self.switch = arcade.SpriteList()
        self.held_letter_cards = []

        self.held_letter_cards_original_position = []

        # ---  Create the mats the cards go on.

        # Sprite list with all the mats tha cards lay on.
        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        # Create the piles/mats
        for i in range(5):
            pile = arcade.SpriteSolidColor(105, 105, arcade.csscolor.DARK_OLIVE_GREEN)
            pile.position = 100 + i * 126, 415
            self.pile_mat_list.append(pile)

        for x in range(0, 40, 4):
            letter_card = LetterCard(x)
            letter_card.position = 65 + x * 16, 262
            setattr(letter_card, 'og_position', letter_card.position)
            self.letter_card_list.append(letter_card)

        # Create LetterCards and place them
        for x in range(40, 76, 4):
            letter_card = LetterCard(x)
            letter_card.position = (x * 16) - 540, 180
            setattr(letter_card, 'og_position', letter_card.position)
            self.letter_card_list.append(letter_card)

        for x in range(76, 104, 4):
            letter_card = LetterCard(x)
            letter_card.position = (x * 16) - 1052, 98
            setattr(letter_card, 'og_position', letter_card.position)
            self.letter_card_list.append(letter_card)

        # Create a list of lists, each holds a pile of cards.
        self.piles = [[] for _ in range(PILE_COUNT)]

        # Green Yellow Switch handling
        self.green_yellow.on_click = self.gy_clicked
        self.manager.add(self.green_yellow)

        # Manager/handling clear and forward
        self.manager.add(self.clear_button)
        self.clear_button.on_click = self.clear_

        self.manager.add(self.forward_button)
        self.forward_button.on_click = self.forward

    # Pile Management methods
    def pile_for_card(self, letter_card):
        """ What pile is this card in? """
        for index, pile in enumerate(self.piles):
            if letter_card in pile:
                return index

    def remove_card_from_pile(self, letter_card):
        """ Remove card from whatever pile it was in. """
        for pile in self.piles:
            if letter_card in pile:
                pile.remove(letter_card)
                break

    def move_card_to_new_pile(self, letter_card, pile_index):
        """ Move the card to a new pile """
        self.remove_card_from_pile(letter_card)
        self.piles[pile_index].append(letter_card)

    # UIEvent methods
    def gy_clicked(self, *_):
        """ When green/yellow toggle button is clicked """
        self.green_or_yellow = not self.green_or_yellow

        self.green_yellow.texture = arcade.load_texture(
            os.path.join('assets', f"{int(self.green_or_yellow)}.png"))

    def clear_(self, *_):
        self.setup()

    def forward(self, *_):
        morklagda = []
        grona = []
        gula = []
        for x in self.letter_card_list:
            if getattr(x, 'zero_or_one'):
                morklagda.append(getattr(x, 'letter'))
        for x in range(100,630,126):
            objlist = arcade.get_sprites_at_point((x,415), self.letter_card_list)
            for i in objlist:
                if getattr(i, 'what_color_is_this') == 'green':
                    grona.append(tuple([getattr(i,'letter'),  getattr(i, 'mat_index')]))
                else:
                    gula.append(tuple([getattr(i,'letter'),  getattr(i, 'mat_index')]))
        f = open("wordfile.txt", "r")
        word_list = [ele for ele in f.read().splitlines() if all(ch not in ele for ch in morklagda)]
        f.close()

        for x,y in grona:
            word_list = [ele for ele in word_list if str(x) == ele[y]]

        for x,y in gula:
            word_list = [ele for ele in word_list if x in ele]
            word_list = [ele for ele in word_list if str(x) != ele[y]]
        messagebox = gui.UIMessageBox(width=450,height=450, message_text=str(word_list))
        self.manager.add(messagebox)

    # Draw/Render order methods
    def on_draw(self):
        self.clear()

        # Draw letter cards
        self.pile_mat_list.draw()
        self.letter_card_list.draw()
        self.manager.draw()

    def pull_to_top(self, letter_card: arcade.Sprite):
        """Pull card to top of rendering order"""

        # Remove, and append to the end
        self.letter_card_list.remove(letter_card)
        self.letter_card_list.append(letter_card)

    # Mouse action methods
    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """

        # Get list of cards we've clicked on
        letter_cards = arcade.get_sprites_at_point((x, y), self.letter_card_list)
        # Have we clicked on a card?
        if len(letter_cards) > 0 and not getattr(letter_cards[-1], 'zero_or_one'):
            # Might be a stack of cards, get the top one
            primary_card = letter_cards[-1]
            assert isinstance(primary_card, LetterCard)

            # All other cases, grab the face-up card we are clicking on
            self.held_letter_cards = [primary_card]
            # Save the position
            self.held_letter_cards_original_position = [self.held_letter_cards[0].position]
            # Put on top in drawing order
            self.pull_to_top(self.held_letter_cards[0])

            # Remove from pile to avoid funny stacking issues
            self.remove_card_from_pile(self.held_letter_cards[0])

        elif len(letter_cards) > 0 and getattr(letter_cards[-1], 'zero_or_one'):
            primary_card = letter_cards[-1]
            assert isinstance(primary_card, LetterCard)
            if not primary_card.is_duplicate:
                primary_card.black_or_white()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        for card in self.held_letter_cards:
            card.center_x += dx
            card.center_y += dy

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        if len(self.held_letter_cards) == 0:
            return

        # Attach to the closest pile
        # Find the closest pile, in case we are in contact with more than one
        pile, distance = arcade.get_closest_sprite(self.held_letter_cards[0], self.pile_mat_list)
        reset_position = True

        # See if we are in contact with the closest pile
        if arcade.check_for_collision(self.held_letter_cards[0], pile):
            # What pile is it?
            pile_index = self.pile_mat_list.index(pile)

            #  Is it the same pile we came from?
            if pile_index == self.pile_for_card(self.held_letter_cards[0]):
                # If so, who cares. We'll just reset our position.
                pass

            # For each held card, move it to the pile we dropped on
            for i, dropped_card in enumerate(self.held_letter_cards):
                assert isinstance(dropped_card, LetterCard)
                # Clone letter card and place clone at og_position
                new_letter_card = LetterCard(dropped_card.nr)
                new_letter_card.position = dropped_card.og_position
                setattr(new_letter_card, 'og_position', new_letter_card.position)
                new_letter_card.is_duplicate = True

                self.letter_card_list.append(new_letter_card)

                if not self.green_or_yellow:
                    if len(self.piles[pile_index]) == 0:
                        dropped_card.green()
                        # Move cards to proper position
                        dropped_card.position = pile.center_x, pile.center_y
                        dropped_card.mat_index = pile_index
                        self.move_card_to_new_pile(dropped_card, pile_index)
                    else:
                        dropped_card.position = dropped_card.og_position
                elif self.green_or_yellow:
                    dropped_card.yellow()
                    dropped_card.mat_index = pile_index
                    # Are there already cards there?
                    if len(self.piles[pile_index]) > 0:
                        # Move cards to proper position
                        top_card = self.piles[pile_index][-1]
                        for i, dropped_card in enumerate(self.held_letter_cards):
                            dropped_card.position = top_card.center_x, \
                                                    top_card.center_y - 15 * (i + 1)
                    else:
                        # Are there no cards in the middle play pile?
                        for i, dropped_card in enumerate(self.held_letter_cards):
                            # Move cards to proper position
                            dropped_card.position = pile.center_x, \
                                                    pile.center_y - 15 * i

                    for card in self.held_letter_cards:
                        # Cards are in the right position, but we need to move them to the right list
                        self.move_card_to_new_pile(card, pile_index)

            # Success, don't reset position of cards
            reset_position = False

        if reset_position:
            primary_card = self.held_letter_cards[-1]
            # Where-ever we were dropped, it wasn't valid. Reset each card's position
            # to its original spot.
            if getattr(primary_card, 'og_position') != self.held_letter_cards_original_position[0]:
                for pile_index, card in enumerate(self.held_letter_cards):
                    card.position = getattr(card, 'og_position')
                    assert isinstance(card, LetterCard)
                    card.white()
                    # card.position = self.held_letter_cards_original_position[pile_index]
                    self.remove_card_from_pile(card)
            # Switch from white to black by pressing, but only when the og position is the same as original position.
            if len(self.held_letter_cards) == 1 and self.held_letter_cards_original_position[0] == getattr(primary_card,
                                                                                                           'og_position'
                                                                                                           ):
                assert isinstance(primary_card, LetterCard)
                primary_card.position = getattr(primary_card, 'og_position')
                if not getattr(primary_card, 'is_duplicate'):
                    primary_card.black_or_white()
                self.remove_card_from_pile(primary_card)
        self.held_letter_cards = []


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
