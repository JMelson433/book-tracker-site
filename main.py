from drafter import *
from dataclasses import dataclass
from bakery import assert_equal


GENRES = [
    "Fantasy",
    "Romance",
    "Mystery",
    "Science Fiction",
    "Nonfiction",
    "Other"
]

PROGRESS_OPTIONS = [
    "Want to Read",
    "Currently Reading",
    "Finished"
]

POINTS_PER_BOOK = 10


@dataclass
class Book:
    author: str
    title: str
    pages: int
    progress: str
    genre: str
    current_page: int
    review: str
    points_awarded: bool


@dataclass
class State:
    books: list[Book]
    points: int
    goal: int
    books_completed: int


#----------------------------
# HELPER FUNCTIONS
#----------------------------

def find_book_index(books: list[Book], title: str) -> int:
    """
    Uses the book's title to assign the corresponding book with a numerated index.
    
    Args:
        books(list[Book]): a list of the user's book entries
        title(str): the title of the book
        
    Return:
        int: a number corresponding to the book's index
    """
    for index, book in enumerate(books):
        if book.title.lower() == title.lower():
            return index
    return -1


def filter_finished_books(books: list[Book]) -> list[Book]:
    """
    Creates a list for just the user's finished books. 
    
    Args:
        books(list{Book]):a list of the user's book entries
    
    Return:
        list[Book]:a list of the user's finished book entries
    """
    finished = []

    for book in books:
        if book.progress == "Finished":
            finished.append(book)

    return finished


def filter_books_by_genre(
    books: list[Book],
    genre: str
) -> list[Book]:
    """
    Creates a list of the books that have the same genre as the user's selection. 
    
    Args:
        books(list[Book]): a list of the user's book entries
        genre(str): the genre of the book
        
    Return:
        list[Book]: a list of the user's book entries with the same genre
    """
    matching_books = []

    for book in books:
        if book.genre == genre:
            matching_books.append(book)

    return matching_books


def calculate_total_pages(books: list[Book]) -> int:
    """
    Calculates the total number of pages read.
    
    Args:
        books(list[Book]): a list of the user's book entries
        
    Return:
        int: total pages read
    """
    total = 0

    for book in books:
        total += book.current_page

    return total


def calculate_average_pages(books: list[Book]) -> float:
    """
    Calculates the average pages read per book.
    
    Args:
        books(list[Book]): a list of the user's book entries
        
    Return:
        float: the average pages read 
    """
    if len(books) == 0:
        return 0.0

    total = calculate_total_pages(books)
    return total / len(books)


def count_finished(books: list[Book]) -> int:
    """
    Determines the number of finished books. 
    
    Args:
        books(list[Book]): a list of the user's book entries
        
    Return:
        int: the total number of completed books
    """
    count = 0

    for book in books:
        if book.progress == "Finished":
            count += 1

    return count


def most_finished_genre(books: list[Book]) -> str:
    """
    Finds the genre with the most finished books.
    
    Args:
        books(list[Book]): a list of the user's book entries
        
    Return:
        str: a genre 
    """
    best_genre = "No finished books yet."
    highest_count = 0

    for genre in GENRES:
        genre_count = 0

        for book in books:
            if book.genre == genre and book.progress == "Finished":
                genre_count += 1

        if genre_count > highest_count:
            highest_count = genre_count
            best_genre = genre

    return best_genre


def award_points(state: State) -> State:
    """
    Award points for each finished book only once.
    
    Args:
        state(State):the current state application of the site
        
    Return:
        State: the updated state application with the new point value 
    """
    completed = 0

    for book in state.books:
        if book.progress == "Finished":
            completed += 1

            if not book.points_awarded:
                state.points += POINTS_PER_BOOK
                book.points_awarded = True

    state.books_completed = completed
    return state

#------------------------------------
# HOME PAGE
#------------------------------------

@route
def index(state: State) -> Page:
    """
    Displays the home page and book tracker navigation to the user. 
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    
    """
    content = [
        Header("My Book Tracker"),
        "Welcome to your own personal book tracker!" + "\n",
        "Are you ready to build your own library, while trying to collect the most points possible?",
        HorizontalRule(),
        Header("Your Reading Summary", 2),
        BulletedList([
            "Books in your tracker: " + str(len(state.books)),
            "Books completed: " + str(state.books_completed),
            "Points earned: " + str(state.points),
            "Reading goal: " + str(state.goal) + " books"
        ]),
        HorizontalRule(),
        Header("Book Tracker Pages", 2),
        Button("Add a Book", "add_book"),
        Button("View All Books", "all_books"),
        Button("View Finished Books", "filter_finished"),
        Button("Filter by Genre", "filter_genre"),
        Button("Update Reading Progress", "update_progress"),
        Button("Add a Book Review", "add_review"),
        Button("Update Points", "update_points"),
        Button("View Statistics", "total"),
        Button("View Average Pages", "average_page")
    ]

    return Page(state, content)


# --------------------------------------------------
# ADDING BOOKS
# --------------------------------------------------

@route
def add_book(state: State) -> Page:
    """
    Currates a form for the user to fill out to add an entry to their tracker.
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    """
    content = [
        Header("Add a New Book"),

        Text("Enter the book's title:"),
        TextBox("title", ""),
        
        "\n",
        
        Text("Enter the author's name:"),
        TextBox("author", ""),
        
        "\n",
        
        Text("Enter the total number of pages:"),
        TextBox("pages", "1"),
        
        "\n",
        
        Text("Enter the current page you have read:"),
        TextBox("current_page", "0"),
        
        "\n",
        
        Text("Select your reading progress:"),
        SelectBox(
            "progress",
            ["Select progress"] + PROGRESS_OPTIONS,
            "Select progress"
        ),
        
        Text("Select a genre:"),
        SelectBox(
            "genre",
            ["Select a genre"] + GENRES,
            "Select a genre"
        ),
        
        "\n",
        
        Button("Save Book", "save_book"),
        Button("Back Home", "index")
    ]

    return Page(state, content)


@route
def save_book(
    state: State,
    title: str,
    author: str,
    pages: int,
    current_page: int,
    genre: str,
    progress: str
) -> Page:
    """
    Ensures the user filled out the entire form before adding the book to the tracker. 
    
    Args:
        state(State): the current state application of the site
        title(str): the title of the book 
        author(str): the author of the book 
        pages(int): the length of the book
        current_page(int): how far the user is into the book
        genre(str): the genre of the book
        progress(str): whether the user hasn't started, is in progress, or finished a book.
    
    Return:
        Page:The content of the state displayed to the user 
    
    """

    # Check that the title and author are entered.
    if title.strip() == "" or author.strip() == "":
        return Page(state, [
            Header("Missing Information"),
            "Please enter both a title and an author.",
            Button("Try Again", "add_book")
        ])

    # Check that a genre was selected.
    if genre == "Select a genre":
        return Page(state, [
            Header("Missing Genre"),
            "Please select a genre for your book.",
            Button("Try Again", "add_book")
        ])

    # Check that reading progress was selected.
    if progress == "Select progress":
        return Page(state, [
            Header("Missing Progress"),
            "Please select your reading progress.",
            Button("Try Again", "add_book")
        ])

    # Check that the total page count is valid.
    if pages <= 0:
        return Page(state, [
            Header("Invalid Page Count"),
            "The total number of pages must be greater than zero.",
            Button("Try Again", "add_book")
        ])

    # Keep the current page within the book's page count.
    if current_page < 0:
        current_page = 0

    if current_page > pages:
        current_page = pages

    if progress == "Finished" or current_page == pages:
        progress = "Finished"
        current_page = pages

    # Create and save the new book.
    new_book = Book(
        author,
        title,
        pages,
        progress,
        genre,
        current_page,
        "",
        False
    )

    state.books.append(new_book)
    state = award_points(state)

    return Page(state, [
        Header("Book Added!"),
        title + " has been added to your tracker.",
        Button("View All Books", "all_books"),
        Button("Back Home", "index")
    ])


# --------------------------------------------------
# VIEWING AND FILTERING BOOKS
# --------------------------------------------------

@route
def all_books(state: State) -> Page:
    """
    Displays every book in the tracker.
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    """
    content = [
        Header("All My Books"),
        Table(state.books),
        Button("Add Another Book", "add_book"),
        Button("Back Home", "index")
    ]

    return Page(state, content)


@route
def filter_finished(state: State) -> Page:
    """
    Displays only the finished books.
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    
    """
    finished_books = filter_finished_books(state.books)

    content = [
        Header("Finished Books"),
        "You have finished " + str(len(finished_books)) + " books.",
        Table(finished_books),
        Button("Back to All Books", "all_books"),
        Button("Back Home", "index")
    ]

    return Page(state, content)


@route
def filter_genre(state: State) -> Page:
    """
    Lets the user decide which genre the tracker will be filtered by.
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    """
    content = [
        Header("Filter Books by Genre"),
        "Choose a genre to see matching books.",
        SelectBox(
            "genre",
            ["Select a genre"] + GENRES,
            "Select a genre"
        ),
        Button("Show Books", "show_genre"),
        Button("Back Home", "index")
    ]

    return Page(state, content)


@route
def show_genre(state: State, genre: str) -> Page:
    """
    Displays only the books that have the corresponding selected genre.
    
    Args:
        state(State):the current state application of the site
        genre(str):the genre of the book
        
    Return:
        Page:The content of the state displayed to the user 
    
    """
    if genre == "Select a genre":
        return Page(state, [
            Header("No Genre Selected"),
            "Please choose a genre first.",
            Button("Try Again", "filter_genre")
        ])

    matching_books = filter_books_by_genre(state.books, genre)
    finished_count = count_finished(matching_books)

    content = [
        Header(genre + " Books"),
        "Books in this genre: " + str(len(matching_books)) + "\n",
        "Finished books in this genre: " + str(finished_count),
        Table(matching_books),
        Button("Choose Another Genre", "filter_genre"),
        Button("Back Home", "index")
    ]

    return Page(state, content)


# --------------------------------------------------
# UPDATING READING PROGRESS
# --------------------------------------------------

@route
def update_progress(state: State) -> Page:
    """
    Displays a form where the user can update a book's progress.
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    """
    content = [
        Header("Update Reading Progress"),
        "Enter the exact title of the book you want to update." +"\n",
        
        Text("Enter the book's title:"),
        TextBox("title", ""),
        
        "\n",
        
        Text("Enter your current page:"),
        TextBox("current_page", "0"),
        
        "\n",
        
        Text("Update your progress:"),
        SelectBox(
            "progress",
            PROGRESS_OPTIONS,
            PROGRESS_OPTIONS[1]
        ),
        
        "\n",
        
        Button("Save Progress", "save_progress"),
        Button("Back Home", "index")
    ]

    return Page(state, content)


@route
def save_progress(
    state: State,
    title: str,
    current_page: int,
    progress: str
) -> Page:
    """
    Updates a chosen book's reading progress 
    
    Args:
        state(State): the current state application of the site
        title(str): the title of the book
        current_page(int): how far the user is into the book
        progress(str):whether the user hasn't started, is in progress, or finished a book
    
    Return:
        Page:The content of the state displayed to the user 
    """
    book_index = find_book_index(state.books, title)

    if book_index == -1:
        return Page(state, [
            Header("Book Not Found"),
            "Check the title and try again.",
            Button("Try Again", "update_progress")
        ])

    book = state.books[book_index]

    if current_page < 0:
        current_page = 0

    if current_page > book.pages:
        current_page = book.pages

    if progress == "Finished" or current_page == book.pages:
        progress = "Finished"
        current_page = book.pages

    book.current_page = current_page
    book.progress = progress

    state = award_points(state)

    return Page(state, [
        Header("Progress Updated!"),
        title + " has been updated.",
        Button("View All Books", "all_books"),
        Button("Back Home", "index")
    ])


# --------------------------------------------------
# BOOK REVIEWS
# --------------------------------------------------

@route
def add_review(state: State) -> Page:
    """
    Displays a form that allows the user to write a book review.
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    """
    content = [
        Header("Write a Book Review"),
        Text("Feel free to share your thoughts about a book!"),
        
        "\n",
        
        Text("Enter the book's title:"),
        TextBox("title", ""),

        "\n",
        
        Text("Write your review:"),
        TextArea("review", ""),
        
        "\n",
        
        Button("Save Review", "save_review"),
        Button("Back Home", "index")
    ]

    return Page(state, content)


@route
def save_review(state: State, title: str, review: str) -> Page:
    """
    Saves the user's review for a chosen book. 
    
    Args:
        state(State): the current state application of the site
        title(str): the title of the book
        review(str): the user's comments on the book
        
    Return:
        Page:The content of the state displayed to the user 
    """
    book_index = find_book_index(state.books, title)

    if book_index == -1:
        return Page(state, [
            Header("Book Not Found"),
            "Check the title and try again.",
            Button("Try Again", "add_review")
        ])

    state.books[book_index].review = review

    return Page(state, [
        Header("Review Saved!"),
        "Your review for " + title + " has been saved.",
        Button("View All Books", "all_books"),
        Button("Back Home", "index")
    ])


# --------------------------------------------------
# POINTS AND STATISTICS
# --------------------------------------------------

@route
def update_points(state: State) -> Page:
    """
    Checks if the book is finished and awards points accordingly.
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    """
    state = award_points(state)

    content = [
        Header("Your Points"),
        "You earn 10 points for each finished book.",
        BulletedList([
        "Books completed: " + str(state.books_completed),
        "Points earned: " + str(state.points)
        ]),
        Button("Back Home", "index")
    ]

    return Page(state, content)


@route
def total(state: State) -> Page:
    """
    Displays the user's acculumated reading statistics.
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    """
    total_pages = calculate_total_pages(state.books)
    finished_count = count_finished(state.books)
    favorite_genre = most_finished_genre(state.books)

    content = [
        Header("Reading Statistics"),
        BulletedList([
        "Total books: " + str(len(state.books)),
        "Books completed: " + str(finished_count),
        "Total pages read: " + str(total_pages),
        "Reading goal: " + str(state.goal),
        "Points earned: " + str(state.points),
        "Genre with the most finished books: " + favorite_genre
        ]),
        Button("Back Home", "index")
    ]

    return Page(state, content)

@route
def average_page(state: State) -> Page:
    """
    Displays the average number of pages read per book.
    
    Args:
        state(State):the current state application of the site
    
    Return:
        Page:The content of the state displayed to the user 
    """
    average = calculate_average_pages(state.books)
    total_pages = calculate_total_pages(state.books)

    content = [
        Header("Average Pages Read"),
        BulletedList([
        "Total pages read: " + str(total_pages),
        "Number of books: " + str(len(state.books)),
        "Average pages per book: " + str(round(average, 2))
        ]),
        Button("Back Home", "index")
        
    ]

    return Page(state, content)


#---------------------------------------
# UNIT TESTS
#---------------------------------------

def make_test_state() -> State:
    """Create sample data for testing."""
    finished_book = Book(
        "Author One",
        "Finished Book",
        200,
        "Finished",
        "Fantasy",
        200,
        "A great book.",
        True
    )

    reading_book = Book(
        "Author Two",
        "Reading Book",
        300,
        "Currently Reading",
        "Mystery",
        100,
        "",
        False
    )

    return State(
        [finished_book, reading_book],
        10,
        12,
        1
    )


def test_find_book_index() -> None:
    """Test finding books by title."""
    state = make_test_state()

    assert_equal(
        find_book_index(state.books, "Finished Book"),
        0
    )
    assert_equal(
        find_book_index(state.books, "Reading Book"),
        1
    )
    assert_equal(
        find_book_index(state.books, "Missing Book"),
        -1
    )


def test_filter_finished_books() -> None:
    """Test filtering for finished books."""
    state = make_test_state()
    result = filter_finished_books(state.books)

    assert_equal(len(result), 1)
    assert_equal(result[0].title, "Finished Book")


def test_filter_books_by_genre() -> None:
    """Test filtering books by genre."""
    state = make_test_state()
    result = filter_books_by_genre(state.books, "Mystery")

    assert_equal(len(result), 1)
    assert_equal(result[0].title, "Reading Book")


def test_calculate_total_pages() -> None:
    """Test adding the pages read across all books."""
    state = make_test_state()

    assert_equal(calculate_total_pages(state.books), 300)


def test_calculate_average_pages() -> None:
    """Test calculating the average pages read."""
    state = make_test_state()

    assert_equal(calculate_average_pages(state.books), 150.0)
    assert_equal(calculate_average_pages([]), 0.0)


def test_count_finished() -> None:
    """Test counting finished books."""
    state = make_test_state()

    assert_equal(count_finished(state.books), 1)


def test_most_finished_genre() -> None:
    """Test finding the genre with the most finished books."""
    state = make_test_state()

    assert_equal(most_finished_genre(state.books), "Fantasy")
    assert_equal(most_finished_genre([]), "No finished books yet.")


def test_award_points() -> None:
    """Test awarding points only once per finished book."""
    book = Book(
        "Author",
        "New Finished Book",
        100,
        "Finished",
        "Romance",
        100,
        "",
        False
    )

    state = State([book], 0, 5, 0)

    state = award_points(state)
    assert_equal(state.points, 10)
    assert_equal(state.books_completed, 1)
    assert_equal(book.points_awarded, True)

    state = award_points(state)
    assert_equal(state.points, 10)


def test_index_route() -> None:
    """Test that the home route keeps the state."""
    state = make_test_state()

    page = index(state)

    assert_equal(page.state, state)


def test_add_book_route() -> None:
    """Test that the add-book form keeps the state."""
    state = make_test_state()

    page = add_book(state)

    assert_equal(page.state, state)


def test_save_book_route() -> None:
    """Test adding a new book."""
    state = make_test_state()

    page = save_book(
        state,
        "New Book",
        "New Author",
        150,
        0,
        "Romance",
        "Want to Read"
    )

    assert_equal(len(page.state.books), 3)
    assert_equal(page.state.books[2].title, "New Book")
    assert_equal(page.state.points, 10)


def test_all_books_route() -> None:
    """Test that the all-books route keeps the state."""
    state = make_test_state()

    page = all_books(state)

    assert_equal(page.state, state)


def test_filter_finished_route() -> None:
    """Test that the finished-books route keeps the state."""
    state = make_test_state()

    page = filter_finished(state)

    assert_equal(page.state, state)


def test_filter_genre_route() -> None:
    """Test that the genre form keeps the state."""
    state = make_test_state()

    page = filter_genre(state)

    assert_equal(page.state, state)


def test_show_genre_route() -> None:
    """Test displaying books from a selected genre."""
    state = make_test_state()

    page = show_genre(state, "Fantasy")

    assert_equal(page.state, state)


def test_update_progress_route() -> None:
    """Test that the progress form keeps the state."""
    state = make_test_state()

    page = update_progress(state)

    assert_equal(page.state, state)


def test_save_progress_route() -> None:
    """Test updating a book and awarding completion points."""
    state = make_test_state()

    page = save_progress(
        state,
        "Reading Book",
        300,
        "Finished"
    )

    assert_equal(page.state.books[1].progress, "Finished")
    assert_equal(page.state.books[1].current_page, 300)
    assert_equal(page.state.points, 20)
    assert_equal(page.state.books_completed, 2)


def test_add_review_route() -> None:
    """Test that the review form keeps the state."""
    state = make_test_state()

    page = add_review(state)

    assert_equal(page.state, state)


def test_save_review_route() -> None:
    """Test saving a review for an existing book."""
    state = make_test_state()

    page = save_review(
        state,
        "Reading Book",
        "I am enjoying this book!"
    )

    assert_equal(
        page.state.books[1].review,
        "I am enjoying this book!"
    )


def test_update_points_route() -> None:
    """Test that the points route awards missing points."""
    book = Book(
        "Author",
        "Finished Book",
        100,
        "Finished",
        "Fantasy",
        100,
        "",
        False
    )

    state = State([book], 0, 5, 0)

    page = update_points(state)

    assert_equal(page.state.points, 10)
    assert_equal(page.state.books_completed, 1)


def test_total_route() -> None:
    """Test that the statistics route keeps the state."""
    state = make_test_state()

    page = total(state)

    assert_equal(page.state, state)


def test_average_page_route() -> None:
    """Test that the average-pages route keeps the state."""
    state = make_test_state()

    page = average_page(state)

    assert_equal(page.state, state)


# --------------------------------------------------
# START THE WEBSITE
# --------------------------------------------------

start_server(State([], 0, 12, 0))

