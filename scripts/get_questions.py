from bs4 import BeautifulSoup
from requests import get
import asyncio as aio
import aiohttp
import aiofiles
import logging
from tqdm import tqdm
import json
import unicodedata

PUZZLES_JSON = 'puzzles.json'
logging.basicConfig()
logger = logging.getLogger("puzzler")
logger.setLevel(logging.DEBUG)

def extract_text(text:str, puzzle:dict):
    first_half, second_half = text.split("Answer\n")
    
    # Extract Question and Hints
    first_splits = first_half.split("Hint\n")
    puzzle["Question"] = first_splits[0].split("Question\n")[1].strip()
    if len(first_splits) == 2:
        puzzle["Hint"] = first_splits[1].strip()
    
    # Extract Answer and Solution
    second_splits = second_half.split("Solution\n")
    puzzle["Answer"] = second_splits[0].strip()
    if len(second_splits) == 2:
        puzzle["Solution"] = second_splits[1].strip()
    
    for key in ["Question", "Hint", "Answer", "Solution"]:
        if (key in puzzle.keys()) and (len(puzzle[key]) == 0):
            puzzle.pop(key)


async def get_text(session:aiohttp.ClientSession, puzzle: dict):
    async with session.get(f"https://brainstellar.com/page-data/puzzles/{puzzle['difficulty']}/{str(puzzle['id'])}/page-data.json") as r:
        if r.status != 200:
            logger.error(f"Puzzle with id {puzzle['id']} and difficulty {puzzle['difficulty']} cannot be stored")
        else:
            resp = await r.json()
            html = resp['result']['data']['markdownRemark']['html']
            soup = BeautifulSoup(html, features="html.parser")
            for tag in soup.find_all('span'):
                if tag.find('annotation'):
                    tag.string = '$' + tag.find('annotation').string + '$'
            text = soup.get_text()
            text = text.replace('\n\n','\n')
            text = text.replace('\n\n','\n')
            text = text.replace('\n\n','\n')
            text = text.replace('\%','%')
            text = text.replace('\&','&')
            text = text.replace('\#','#')
            text = text.replace('%','\%')
            text = text.replace('&','\&')
            text = text.replace('#','\#')
            text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
            extract_text(text, puzzle)
            return puzzle

# Puzzle structure: {'frontmatter': {'puzzleId': 1, 'title': 'Rolling the bullet', 'difficulty': 'easy', 'category': 'probability'}}
def get_puzzles_from_difficulty(difficulty: str):
    r = get(f"https://brainstellar.com/page-data/puzzles/{difficulty}/page-data.json")
    puzzles = r.json()['result']['data']['allMarkdownRemark']['nodes']
    return puzzles

async def get_and_store_puzzles(puzzles: list):
    logger.info("Storing puzzles")
    session = aiohttp.ClientSession()
    coros = []
    for puzzle in tqdm(puzzles):
        coros.append(get_text(session, puzzle))
    
    logger.info("Starting async loop")
    extracted_puzzles = await aio.gather(*coros, return_exceptions=False)
    await session.close()

    # Storing extracted puzzles
    fp = open(PUZZLES_JSON, mode="w")
    json.dump(extracted_puzzles, fp)
    fp.close()

def get_all_puzzles():
    difficulties = ["easy", "medium", "hard", "deadly"]
    puzzle_list = []
    for difficulty in difficulties:
        logger.info(f"Extracting puzzles of {difficulty} difficulty")
        puzzles = get_puzzles_from_difficulty(difficulty)
        for puzzle in tqdm(puzzles):
            puzzle_list.append({
                "id": puzzle["frontmatter"]["puzzleId"],
                "title": puzzle["frontmatter"]["title"],
                "difficulty": difficulty,
                "category": puzzle["frontmatter"]["category"],
            })
    return puzzle_list

if __name__ == "__main__":
    puzzles = get_all_puzzles()
    aio.run(get_and_store_puzzles(puzzles))