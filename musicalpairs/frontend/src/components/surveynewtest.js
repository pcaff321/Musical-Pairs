import { jssPreset } from '@material-ui/core';
import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom'
import SurveyTest from './surveytest';
// import SurveyTest2 from './surveytest2';
import { Button, Grid, Typography, TextField, FormHelperText, FormControl, FormControlLabel, Radio, RadioGroup, Slider} from '@material-ui/core'
import { createTheme, ThemeProvider } from '@material-ui/core/styles';
import { purple } from '@material-ui/core/colors';
import ProgressBar from 'react-bootstrap/ProgressBar'

<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>

document.body.style = 'background: #f0ffff ;';

var all = document.getElementsByTagName("*");

for (var i=0, max=all.length; i < max; i++) {
 all[i].style.color = "#000000";
} 

const theme = createTheme({
    palette: {
        primary: {
          main: '#1a237e',
        },
        secondary: {
          main: '#0d47a1',
        },
      },
});

function showNextStage(displayedTable, room_count) {
    let newStage = displayedTable + 1;
    if (newStage > room_count + 1) {
        newStage = room_count + 1;
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
    const audioRef = useRef()

    function keyEventListener(e) {
        console.log("oy", answerValue);
        if (e.keyCode == '39') {
            if (isQuestion()) {
                handleSubmitButtonPressed();
            }
            setDisplayedTable(showNextStage(displayedTable, roomData.round_count));
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
        } else if (e.keyCode == '82') {
            let audio = document.querySelector('audio');
            if (typeof(audio) != 'undefined' && audio != null) {
                audio.pause();
                audio.currentTime = 0;
                audio.play();
            }
        }
    }

    function audioSetsNextStage() {
        setDisplayedTable(showNextStage(displayedTable, roomData.round_count));
    }

    function handlePairButtonsPressed(e) {
        let input = document.querySelector("input");
        input.value = e.target.innerText;
        if (e.target.innerText == "DISTRACTED") {
            setAnswerValue("WAS_DISTRACTED");
            input.value = "Distracted";
        } else if (e.target.innerText == "NO IDEA") {
            setAnswerValue("NO_IDEA");
            input.value = "No Idea";
        }
   }

   function subscribeToExperiment(e) {
        e.target.innerText = "Subscribed"
        var fd = new FormData();
        console.log(document.querySelector("#subscribeBtn").value)
        console.log(e.target.value)
        experimentID = document.querySelector("#subscribeBtn").value
        fd.append('experiment_id', experimentID)
        let csrftoken = getCookie('csrftoken');
        let subscribeUrl = "/audio/listExperiments/?id=" + experimentID + "/";
        $.ajax({
            type: 'POST',
            url: subscribeUrl,
            headers: {"X-CSRFToken": csrftoken},
            processData: false,
            data: fd,
            contentType: false
        }).done(function(data) {
            console.log(data);
        });
   }

   function viewResults() {
        let reviewUrl = "/audio/showResults/?id=" + experimentID;
        window.location.href = reviewUrl;
   }

    function handleAnswerChange(e) {
        setAnswerValue(e.target.value);
    }

    function handleSliderChange(e, value) {
        setAnswerValue(value);
    }

    function handleSubmitButtonPressed() {
        let answer = answerValue;
        if (answer == "") {
            if (roomData.round_list[displayedTable][2] == "Yes/No") {
                answer = "Yes";
            } else if (roomData.round_list[displayedTable][2] == "Slider") {
                answer = "0";
            } else if (roomData.round_list[displayedTable][2] == "Agree") {
                answer = "3";
            } else {
                answer = "NOT_ANSWERED"
            }
        }
        let fd = new FormData();
        let csrftoken = getCookie('csrftoken');
        questionID = roomData.round_list[displayedTable][3]
        experimentID = roomData.round_list[displayedTable][4]
        pair_or_question = roomData.round_list[displayedTable][5]
        fd.append('answerValue', answer);
        fd.append('experimentID', experimentID);
        fd.append('questionID',  questionID);
        fd.append('pair_or_question', pair_or_question);

        fetch('/audio/answerQuestion_POST/', {
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            body: fd
        });
        setAnswerValue("");
        setDisplayedTable(showNextStage(displayedTable, roomData.round_count));
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
            audio.play();
            audio.addEventListener("ended", audioSetsNextStage);
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
                audio.pause();
                audio.currentTime = 0;
            }
            if (typeof(submitButton) != 'undefined' && submitButton != null) {
                submitButton.removeEventListener("click", handleSubmitButtonPressed);
            }
        };

    }, [roomCode, setRoomData, roomData.round_count, displayedTable, answerValue])

    if (roomData.round_count != 0 && is_components_set === false) {
        let initial_components = {};
        console.log("ROOM DATA");
        for (let i = 1; i < roomData.round_count + 1; i++) {
            console.log(i, roomData.round_list[i]);
            if (roomData.round_list[i][0] == "text") {
                console.log("hello???")
                console.log(roomData.round_list[i][1]);
                initial_components[i] = (
                    <h1>{roomData.round_list[i][1]}</h1>
                );
                let paragraph_list = roomData.round_list[i].splice(2);
                initial_components[i] = (
                    <div align="center">
                        {initial_components[i]}
                        {paragraph_list.map((item, index) => (
                            <p><strong>{item}</strong></p>
                        ))}
                    </div>
                )
            } else if (roomData.round_list[i][0] == "audio") {
                initial_components[i] = (
                    <div>
                        <Grid item xs={12} align="center">
                            <img src="/media/CloseYourEyes.png" style={{ height: "80%", width: "80%", 'object-fit': "contain", top: "1em", position: "relative" }}></img>
                        </Grid><br></br><br></br>
                        <h2 style={{ textAlign: "center" }}><strong>Please Close Your Eyes </strong></h2>
                        <audio controls autoPlay hidden src={roomData.round_list[i][4]}>
                            <source src={roomData.round_list[i][4]} type="audio/wav"></source>
                        </audio>
                    </div>
                );
            } else if (roomData.round_list[i][0] == "question") {
                let question;
                experimentID = roomData.round_list[i][4];
                if (roomData.round_list[i][2] == "Yes/No") {
                    question = (
                        <Grid item xs={12} align="center">
                            <RadioGroup row defaultValue="Yes" onChange={handleAnswerChange} style={{ display: "block" }}>
                                <FormControlLabel 
                                    value="Yes" control={<Radio color="primary" />} 
                                    label="Yes" labelPlacement="bottom"
                                />
                                <FormControlLabel 
                                    value="No" control={<Radio color="secondary" />} 
                                    label="No" labelPlacement="bottom"
                                />
                            </RadioGroup>
                        </Grid>
                    );
                } else if (roomData.round_list[i][2] == "Agree") {
                    question = (
                        <RadioGroup id="agree" row defaultValue="3" onChange={handleAnswerChange} style={{ display: "block" }}>
                            <FormControlLabel 
                                value="1" control={<Radio color="primary" />} 
                                label="1" labelPlacement="bottom"
                            />
                            <FormControlLabel 
                                value="2" control={<Radio color="primary" />} 
                                label="2" labelPlacement="bottom"
                            />
                            <FormControlLabel 
                                value="3" control={<Radio color="primary" />} 
                                label="3" labelPlacement="bottom"
                            />
                            <FormControlLabel 
                                value="4" control={<Radio color="primary" />} 
                                label="4" labelPlacement="bottom"
                            />
                            <FormControlLabel 
                                value="5" control={<Radio color="primary" />} 
                                label="5" labelPlacement="bottom"
                            />
                        </RadioGroup>
                    );
                } else if (roomData.round_list[i][2] == "Slider") {
                    let max = 10;
                    let min = 0;
                    const marks = [
                        { value: 0, label: '0'},
                        { value: 1, label: '1'},
                        { value: 2, label: '2'},
                        { value: 3, label: '3'},
                        { value: 4, label: '4'},
                        { value: 5, label: '5'},
                        { value: 6, label: '6'},
                        { value: 7, label: '7'},
                        { value: 8, label: '8'},
                        { value: 9, label: '9'},
                        { value: 10, label: '10'},
                      ];
                    question = <Slider defaultValue={0} marks={marks} valueLabelDisplay="auto"
                                max={max} min={min} onChange={handleSliderChange} />
                } else if (roomData.round_list[i][2] == "Text") {
                    question = (
                        <TextField 
                            required={true} type="text"
                            inputProps={{style: { textAlign: "center" }}}
                            onChange={handleAnswerChange}
                        />
                    );
                } else {
                    question = <p>placeholder--unaccounted for question type</p> 
                }
                console.log(roomData.round_list[i][5]);
                if (roomData.round_list[i][5] == "question") {
                    initial_components[i] = (
                        <Grid item xs={12} align="center">
                            <FormControl component="fieldset" style={{ minWidth: "50%" }}>
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
                } else {
                    initial_components[i] = (
                        <ThemeProvider theme={theme}>
                            <Grid item xs={12} align="center">
                                <FormControl component="fieldset">
                                    <h1>
                                        {roomData.round_list[i][1]}
                                    </h1>
                                    {question}
                                </FormControl><br></br><br></br><br></br>
                                <Grid item xs={12} align="center">
                                    <Button id="distracted" value="WAS_DISTRACTED" color="secondary" variant="contained"
                                        onClick={handlePairButtonsPressed}>
                                        Distracted
                                    </Button>
                                    <Button id="no-idea" value="NO_IDEA" color="secondary" variant="contained"
                                        onClick={handlePairButtonsPressed}>
                                        No Idea
                                    </Button>
                                </Grid>
                                <br></br>
                                <Grid item xs={12} align="center">
                                    <Button id="submit" color="primary" variant="contained">
                                        Submit
                                    </Button>
                                </Grid>
                                <br></br><br></br>
                                <p><strong>If you were distracted while listening to the audio, press "Distracted".</strong></p>
                                <p><strong>If you have no idea what the answer is, press "No Idea".</strong></p>
                            </Grid>
                        </ThemeProvider>
                    );
                }
            } else if (roomData.round_list[i][0] == "image") {
                    initial_components[i] = (
                        <Grid item xs={12} align="center">
                            <img src={roomData.round_list[i][1]} style={{ height: "60%", width: "80%", 'object-fit': "contain", top: "1em", position: "relative" }}></img>
                        </Grid>
                    )
            } else {
                initial_components[i] = (
                    <div>
                        <h1>Question {i}</h1>
                        <SurveyTest />
                    </div>
                );
            }
        }
        console.log(experimentID);
        let end_page = (
            <ThemeProvider theme={theme}>
                <Grid item xs={12} align="center">
                        <h1>
                            Experiment Complete
                    </h1><br></br><br></br><br></br>
                    <br></br><br></br>
                    <p><strong>Thank you for partaking in this experiment!</strong></p>
                    <p><strong>If you would like to subscribe to updates on the experiment or see a review of your test, please click the corresponding buttons below.</strong></p>
                    <Grid item xs={12} align="center">
                        <Button id="subscribeBtn" name="subscribeBtn" value={experimentID} color="secondary" variant="contained"
                        onClick={subscribeToExperiment}>
                            Subscribe To Updates
                        </Button>
                        <Button id="view-results" value="view-results" color="secondary" onClick={viewResults}>
                            View Your Results
                        </Button>
                    </Grid>
                </Grid>
            </ThemeProvider>
        )
        initial_components[Object.keys(initial_components).length + 1] = end_page;
        console.log("INITIAL COMPONENTS", initial_components);
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
        <Grid container spacing={1} style={{ height: "100vm"}} alignItems="center" justifyContent="center">
            <Grid item xs={12} align="center" style={{textAlign: "center", width: "100%", top: "5%", position: "absolute"}}>
                <h1>{roomData.name}</h1>
            </Grid>
            <div style={{ width: "50%" }}>
                {components[displayedTable]}
            </div>
            <Grid item xs={12} align="center" style={{ textAlign: "center", bottom: "5%", position: "absolute"}}>
                <p>Use the arrow keys to navigate back and forth.</p>
            </Grid>
            <Grid item xs={12} align="right" style={{ marginRight: "1em", textAlign: "right", width: "100%", bottom: "5%", position: "absolute"}}>
                <p>page {displayedTable}/{roomData.round_count + 1}</p>
                <ProgressBar animated now={100 * displayedTable/(roomData.round_count + 1)} style={{width: "30%", marginLeft: "auto", marginRight: "auto", backgroundColor: "darkgray"}}/>
            </Grid>
        </Grid>
    )
}