import { useAuth } from "../context/AuthContext";
import { useCookies } from "react-cookie";
import { API } from "../api/api";
import { Instructions } from "../gameinstructions";
import { createDisabledButtons } from "../utility/utility";
import { useCallback, useEffect, useState } from "react";

const GamePage = () => {
    const [cookies] = useCookies(['AccessToken', 'Player']);
    const [difficulty, setDifficulty] = useState('');
    const [difficultySelector, setDifficultySelector] = useState('Difficulty');
    const [guess, setGuess] = useState([]);
    const [gameRounds, setGameRounds] = useState([]);
    const [leaderboard, setLeaderboard] = useState({})
    const [isWinner, setIsWinner] = useState(false);
    const [isLoser, setIsLoser] = useState(false);
    const [noGame, setNoGame] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const player = cookies.Player;
    const { logout } = useAuth();


    const newGame = async () => {
        /*
        Uses player's cookies to create new game entry
        Re-fetch game stats
        */
        setIsLoser(false);
        setIsWinner(false);
        setIsLoading(true);
        setNoGame(false)
        try {
            const newGameResponse = await API.post(`game/newgame/`, {}, {
                headers: {
                    Authorization: `JWT ${cookies.AccessToken}`,
                },
            });

            if (newGameResponse.status === 201) {
                setErrorMessage('');
                setGuess('')
                await fetchRoundData();
                await fetchDifficulty();
                await fetchLeaderboard();
                setIsLoading(false);
            };
        } catch (error) {
            console.log(error, 'Unable to create new game')
        };
    };


    const handleNumberClick = (num) => {
        if (guess.length >= difficulty) return;
        const updatedGuess = [...guess];
        updatedGuess.push(num);
        setGuess(updatedGuess);
    };


    const handleDeleteClick = () => {
        const updatedGuess = [...guess];
        updatedGuess.pop();
        setGuess(updatedGuess);
    };


    const handleDifficultyChange = (e) => {
        setDifficultySelector(e.target.value);
    };


    const handleSetDifficulty = async () => {
        if (difficultySelector === 'Difficulty') {
            return;
        }
        const difficultyData = {
            difficulty: difficultySelector
        };
        console.log(difficultyData)
        try {
            const difficultyResponse = await API.patch(`game/difficulty/`, difficultyData, {
                headers: {
                    Authorization: `JWT ${cookies.AccessToken}`,
                },
            });

            if (difficultyResponse.status === 200) {
                newGame();
                setDifficultySelector('Difficulty');
            }
        } catch (error) {
            console.log(error, 'Unable to set difficulty');
        };
    };


    const createActiveButtons = () => {
        /*
        Builds number buttons for inputting guess
        Limited from numbers 0-7
        Builds delete and submit button
        */
        const buttonArray = [];
        for (let i = 0; i <= 7; i++) {
            buttonArray.push(<button className='numberbuttons' key={`button-${i}`} onClick={() => handleNumberClick(i)}>{i}</button>);
        };
        buttonArray.push(<button className='deletebutton' key={'delete-button'} onClick={handleDeleteClick}>del</button>);

        return (
            <div className='controls'>
                <div className='controls'><div className='numberbuttoncontainer'>
                    {buttonArray}
                </div>
                    <button className='submitbutton' onClick={handleSubmitClick}>submit</button>
                </div>
            </div>
        );
    };


    const handleSubmitClick = async () => {
        /*
        Uses guess to submit a new round to database
        Re-fetch game stats
        */
        const guessString = guess.join('');
        if (guess.length !== difficulty) {
            setErrorMessage(`Please input ${difficulty} numbers!`)
            return;
        }
        for (let round of gameRounds) {
            if (guessString === round.guess) {
                setErrorMessage(`Please input unique guess!`)
                return;
            }
        }
        setErrorMessage('')
        const guessData = {
            guess: guessString,
        };
        try {
            const submitGuessResponse = await API.post(`game/gamerounds/`, guessData, {
                headers: {
                    Authorization: `JWT ${cookies.AccessToken}`,
                },
            });
            if (submitGuessResponse.status === 201) {
                setGuess([]);
                fetchRoundData();
            };
        } catch (error) {
            console.log(error, 'Unable to fetch profile info')
        };
    };


    const createRounds = () => {
        /*
        Builds components for displaying previous guess information
        Depending on prior guess feedback:
        Win displays You Win component
        Lose displays You Lose component
        */
        if (noGame) {
            return;
        }
        const roundComponents = gameRounds.map((roundData, i) => (
            <div key={`round-${i + 1}`} id={`round-${i + 1}`} className='gameround'>
                <div className='containername'>
                    <span style={{ backgroundColor: 'white' }}>&nbsp;round {i + 1}&nbsp;</span>
                </div>
                <div className='gameinfo'>
                    <div className='gameinfotext'>
                        {roundData.correct_numbers} number(s)
                    </div>
                    <div className='gameinfotext'>
                        {roundData.correct_positions} position(s)
                    </div>
                </div>
                <div className='guess'>
                    {gameRounds[i].guess}
                </div>
            </div>
        ));

        const lastIndex = gameRounds.length + 1;
        if (lastIndex <= 10 && !isWinner && !isLoser) {
            roundComponents.push(
                <div key={`round-${lastIndex}`} id={`round-${lastIndex}`} className='gameround'>
                    <div className='containername'>
                        <span style={{ backgroundColor: 'white' }}>&nbsp;round {lastIndex}&nbsp;</span>
                    </div>
                    <div className='guess'>
                        {guess}
                        <div className='errormessage'>
                            {errorMessage}
                        </div>
                    </div>
                </div>)
        } else {
            if (isWinner) {

                roundComponents.push(
                    <div key={`round-${lastIndex}`} id={`round-${lastIndex}`} className='winner'>
                        You win!
                    </div>)
            } else if (isLoser) {
                roundComponents.push(
                    <div key={`round-${lastIndex}`} id={`round-${lastIndex}`} className='loser'>
                        You lose!
                    </div>)
            }
        }
        return roundComponents;
    }


    const fetchLeaderboard = useCallback(async () => {
        /*
        Fetch total player wins information
        */
        try {
            const leaderBoardResponse = await API.get(`game/leaderboard/`, {
                headers: {
                    Authorization: `JWT ${cookies.AccessToken}`
                }
            })
            if (leaderBoardResponse.status === 200) {
                const data = leaderBoardResponse.data;
                setLeaderboard({ wins: data.wins })
            }
        } catch (error) {
            console.log(error, 'Unable to fetch Rankings')
        }
    }, [cookies.AccessToken])


    const fetchRoundData = useCallback(async () => {
        /*
        Fetch previous guesses from the current game
        Includes the number of correct numbers and correct positions
        */
        try {
            const roundDataResponse = await API.get(`game/gamerounds/`, {
                headers: {
                    Authorization: `JWT ${cookies.AccessToken}`,
                },
            });
            if (roundDataResponse.status === 200) {
                const data = roundDataResponse.data;
                setGameRounds(data);
                setNoGame(false);

                if (data.length === 0) return;

                const lastRound = data[data.length - 1];
                if (lastRound.correct_positions === difficulty) {
                    setIsWinner(true);
                    fetchLeaderboard();
                } else if (data.length === 10) {
                    setIsLoser(true);
                    fetchLeaderboard();
                }
            }
        } catch (error) {
            if (error.status === 404) {
                setNoGame(true);
                console.log(error, 'Unable to fetch round data');
                return;
            }

        }
    }, [cookies.AccessToken, difficulty, fetchLeaderboard]);


    const fetchDifficulty = useCallback(async () => {
        try {
            const playerInfoResponse = await API.get(`game/difficulty/`, {
                headers: {
                    Authorization: `JWT ${cookies.AccessToken}`,
                },
            });
            if (playerInfoResponse.status === 200) {
                const data = playerInfoResponse.data;
                setDifficulty(data);
            };
        } catch (error) {
            console.log(error, 'Unable to fetch profile info')
        };
    }, [cookies.AccessToken]);


    useEffect(() => {
        /*
        INITIALIZE GAME STATUS
        */
        fetchRoundData();
        fetchDifficulty();
        fetchLeaderboard();
    }, [cookies.AccessToken, fetchDifficulty, fetchRoundData, fetchLeaderboard]);


    return (
        <div className='maincontainer'>
            <div className='rankingscontainer'>
                <div className='rankings'>
                    {player}'s level {difficulty} rankings:
                </div>
                <div className='rankings'>
                    Wins: {leaderboard.wins}
                </div>
            </div>
            <div className='wholepagecontainer'>
                <div className='gameboardcontainer'>
                    <div className='gametitlecontainer'>
                        <div className='newgame'>
                            <button onClick={newGame}>new game</button>
                        </div>
                        <div className='gametitle'>
                            MASTERMIND
                        </div>
                    </div>
                    <div className='controlscontainer'>
                        <div className='containername'>
                            <span style={{ backgroundColor: 'white' }}>&nbsp;controls&nbsp;</span>
                        </div>
                        {!isWinner && !isLoser && !noGame && createActiveButtons()}
                        {(isWinner || isLoser || noGame) && createDisabledButtons()}
                    </div>
                    {createRounds()}
                    {isLoading && <div className='loading'>Loading...</div>}
                </div>
            </div>
            <div className='gameinstructionscontainer'>
                <div className='gameinstructions'>
                    {Instructions}
                </div>
                <div className='difficultylabel'>
                    Currently({difficulty})
                </div>
                <div className='miscbuttonscontainer'>
                    <div className='difficulty'>
                        <select value={difficultySelector} onChange={handleDifficultyChange}>
                            <option value='Difficulty' disabled>Difficulty</option>
                            {difficulty !== 4 && <option value="4">4 numbers</option>}
                            {difficulty !== 5 && <option value="5">5 numbers</option>}
                            {difficulty !== 6 && <option value="6">6 numbers</option>}
                        </select>
                        <button onClick={handleSetDifficulty}>Set</button>
                    </div>
                    <button className='logoutbutton' onClick={() => logout(player)}>Logout</button>
                </div>
            </div>
        </div>
    )
}

export default GamePage;