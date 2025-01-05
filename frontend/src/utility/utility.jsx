export const createDisabledButtons = () => {
    /*
    Builds placeholder buttons while player is in win, lose, or no game status 
    */
    const buttonArray = [];
    for (let i = 0; i <= 7; i++) {
        buttonArray.push(<button className='disablednumberbuttons' key={`button-${i}`}>{i}</button>);
    };
    buttonArray.push(<button className='disableddeletebutton' key={'delete-button'}>del</button>);

    return (
        <div className='controls'>
            <div className='controls'>
                <div className='numberbuttoncontainer'>
                    {buttonArray}
                </div>
                <button className='disabledsubmitbutton'>submit</button>
            </div>
        </div>
    )
};

export const convertSeconds = (time) => {
    /*
    Converts a total amount of seconds into a 0:00 timer
    */
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    const timeString = `${minutes}:${seconds < 10 ? `0${seconds}` : seconds}`;
    return timeString;
};