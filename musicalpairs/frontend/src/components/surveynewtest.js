import { jssPreset } from '@material-ui/core';
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'
import SurveyTest from './surveytest';
// import SurveyTest2 from './surveytest2';
import { Button, Grid, Typography, TextField, FormHelperText, FormControl, FormControlLabel, Radio, RadioGroup, Slider} from '@material-ui/core'

function showNextStage(displayedTable, room_count) {
    let newStage = displayedTable + 1;
    if (newStage > room_count) {
        newStage = room_count;
    }
    return newStage;
}

function showPreviousStage(displayedTable) {
    let newStage = displayedTable - 1;
    if (newStage < 1) {
        newStage = 1;
    }
    return newStage;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export default function Survey(props) {
    const initialState = {
        id: 0,
        name: "Default",
        round_count: 0,
        is_host: false
    }
    const [ roomData, setRoomData ] = useState(initialState) 
    const { roomCode } = useParams()
    const [ displayedTable, setDisplayedTable ] = useState(1);
    const [ components, setComponents ] = useState({});
    const [ is_components_set, setIsComponentsSet ] = useState(false)
    const [ answerValue, setAnswerValue ] = useState("")
    let experimentID = "";
    let questionID = "";
    let pair_or_question = "question";

    function keyEventListener(e) {
        console.log("oy", answerValue);
        if (e.keyCode == '39') {
            if (isQuestion()) {
                handleSubmitButtonPressed();
            }
            setDisplayedTable(showNextStage(displayedTable, roomData.round_count));
            setAnswerValue("");
            /* let audio = document.getElementsByTagName("audio")[0];
            if (typeof(audio) != 'undefined' && audio != null) {
                if (audio.ended) {
                    setDisplayedTable(showNextStage(displayedTable, roomData.round_count));
                }
            } else {
                setDisplayedTable(showNextStage(displayedTable, roomData.round_count));
            } */
        } else if (e.keyCode == '37') {
            setDisplayedTable(showPreviousStage(displayedTable));
        }
    }

    function audioSetsNextStage() {
        setDisplayedTable(showNextStage(displayedTable, roomData.round_count));
    }

    function handleAnswerChange(e) {
        setAnswerValue(e.target.value);
    }

    function handleSliderChange(e, value) {
        setAnswerValue(value);
    }

    function handleSubmitButtonPressed() {
        let fd = new FormData();
        let csrftoken = getCookie('csrftoken');
        questionID = roomData.round_list[displayedTable][3]
        experimentID = roomData.round_list[displayedTable][4]
        pair_or_question = roomData.round_list[displayedTable][5]
        fd.append('answerValue', answerValue);
        fd.append('experimentID', experimentID);
        fd.append('questionID',  questionID);
        fd.append('pair_or_question', pair_or_question);

        fetch('/audio/answerQuestion_POST/', {
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            body: fd
        });
    }

    function isQuestion() {
        return (roomData.round_list[displayedTable][0] == "question")
    }

    useEffect(() => {
        fetch("/audio/get-room" + "?code=" + roomCode)
          .then(res => res.json())
          .then(data => {
            setRoomData({
                roomData,
                id: data.id,
                name: data.name,
                round_count: data.round_count,
                round_list: data.round_list,
                is_host: data.is_host,
            })
          })
        
        window.addEventListener('keydown', keyEventListener);

        let audio = document.querySelector('audio');
        if (typeof(audio) != 'undefined' && audio != null) {
            audio.addEventListener("ended", audioSetsNextStage)
        }

        let submitButton = document.getElementById("submit");
        if (typeof(submitButton) != 'undefined' && submitButton != null) {
            submitButton.addEventListener("click", handleSubmitButtonPressed);
        }

        // cleanup this component
        return () => {
            window.removeEventListener('keydown', keyEventListener);
            if (typeof(audio) != 'undefined' && audio != null) {
                audio.removeEventListener("ended", audioSetsNextStage);
            }
            if (typeof(submitButton) != 'undefined' && submitButton != null) {
                submitButton.removeEventListener("click", handleSubmitButtonPressed);
            }
        };

    }, [roomCode, setRoomData, roomData.round_count, displayedTable, answerValue])

    if (roomData.round_count != 0 && is_components_set === false) {
        let initial_components = {};
        console.log("ROOM DATA");
        console.log(roomData.round_list);
        for (let i = 1; i < roomData.round_count + 1; i++) {
            if (roomData.round_list[i][0] == "text") {
                console.log(roomData.round_list[i][1]);
                initial_components[i] = (
                    <h1>{roomData.round_list[i][1]}</h1>
                );
                let paragraph_list = roomData.round_list[i].splice(2);
                initial_components[i] = (
                    <div>
                        {initial_components[i]}
                        {paragraph_list.map((item, index) => (
                            <p>{item}</p>
                        ))}
                    </div>
                )
            } else if (roomData.round_list[i][0] == "audio") {
                initial_components[i] = (
                    <div>
                        <p>Please Close Your Eyes</p>
                        <audio controls autoPlay hidden>
                            <source src={roomData.round_list[i][4]} type="audio/wav"></source>
                        </audio>
                    </div>
                );
            } else if (roomData.round_list[i][0] == "question") {
                let question;
                if (roomData.round_list[i][2] == "Yes/No") {
                    question = (
                        <RadioGroup row defaultValue="Yes" onChange={handleAnswerChange}>
                            <FormControlLabel 
                                value="Yes" control={<Radio color="primary" />} 
                                label="Yes" labelPlacement="bottom"
                            />
                            <FormControlLabel 
                                value="No" control={<Radio color="secondary" />} 
                                label="No" labelPlacement="bottom"
                            />
                        </RadioGroup>
                    )
                } else if (roomData.round_list[i][2] == "Slider") {
                    question = <Slider marks onChange={handleSliderChange} />
                } else if (roomData.round_list[i][2] == "Text") {
                    question = (
                        <TextField 
                            required={true} type="text"
                            inputProps={{style: {textAlign: "center"}}}
                            onChange={handleAnswerChange}
                        />
                    )
                } else {
                    question = <p>placeholder--unaccounted for question type</p> 
                }
                initial_components[i] = (
                    <Grid item xs={12} align="center">
                        <FormControl component="fieldset">
                            <h1>
                                {roomData.round_list[i][1]}
                            </h1>
                            {question}
                        </FormControl>
                        <Grid item xs={12} align="center">
                            <Button id="submit" color="primary" variant="contained">
                                Submit
                            </Button>
                        </Grid>
                    </Grid>
                );
            } else if (roomData.round_list[i][0] == "image") {
                initial_components[i] = <img src={roomData.round_list[i][1]}></img>
            } else {
                initial_components[i] = (
                    <div>
                        <h1>Question {i}</h1>
                        <SurveyTest />
                    </div>
                );
            }
        }
        setIsComponentsSet(true);
        setComponents(initial_components);
    }

    return (
    //   <div>
    //     <h3>{roomCode}</h3>
    //     <p>Votes: {roomData.votes_to_skip}</p>
    //     <p>RoundCount: {roomData.round_count}</p>
    //     <p>RoundList: {roomData.round_list}</p>  
    //     <p>Guest: {roomData.guest_can_pause.toString()}</p>
    //     <p>Host: {roomData.is_host.toString()}</p>
    //   </div>
        <Grid container spacing={1} style={{ height: "75%" }} alignItems="center" justifyContent="center">
            <Grid item xs={12} align="center">
                <h1>{roomData.name}</h1>
            </Grid>
            {components[displayedTable]}
        </Grid>
    )
  }