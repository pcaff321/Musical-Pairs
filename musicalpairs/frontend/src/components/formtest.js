import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Button, Grid, Typography, Slider, TextField, FormHelperText, FormControl, FormControlLabel, Radio, RadioGroup} from '@material-ui/core'

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

export default class FormTest extends Component {

    constructor(props) {
        super(props);
        this.state = {
            experimentID: "",
            answerValue: "",
            questionID: ""
        };
        let sliderValue = 0;
    }


    // handleVotesChange = (e) => {
    //     this.setState({
    //         votes_to_skip: e.target.value
    // });
    // }

    // handleGuestCanPauseChange = (e) => {
    //     this.setState({
    //         guest_can_pause: e.target.value === true ? true : false
    //     });
    // }

    handleRoundCountChange = (e) => {
        this.setState({
            round_count: e.target.value
        });
    }

    handleAnswerChange = (e) => {
        this.setState({
            answerValue: e.target.value
        });
    }

    handleSliderChange = (e, value) => {
        this.setState({
            answerValue: value
        });
    }

    handleSurveyButtonPressed = () => {
        let fd = new FormData();
        let csrftoken = getCookie('csrftoken');
        console.log(this.state.answerValue);
        fd.append('answerValue',  this.state.answerValue);
        fd.append('experimentID',  this.state.experimentID);
        fd.append('questionID',  this.state.questionID);

        fetch('/answerQuestion_POST', {
            method: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            body: fd
        });
    }

    render() {
        return (
            <Grid container spacing={1} style={{ height: "75%" }} alignItems="center" justifyContent="center">

                <Grid item xs={12} align="center">
                    <Typography component="h4" variant="h4">
                        Create a Survey
                    </Typography>
                </Grid>

                <Grid item xs={12} align="center">
                <FormControl>
                        <TextField 
                            required={true} type="text"
                            inputProps={{style: {textAlign: "center"}}}
                            onChange={this.handleAnswerChange}
                        />
                        <FormHelperText>
                           Answer
                        </FormHelperText>
                    </FormControl>
                </Grid>

                <Grid item xs={12} align="center">
                    <Button color="secondary" variant="contained" onClick={this.handleSurveyButtonPressed}>
                        Start Experiment
                    </Button>
                </Grid>

                <Grid item xs={12} align="center">
                    <Button color="primary" variant="contained" to="/" component={Link}>
                        Back
                    </Button>
                </Grid>

            </Grid>
        );
    }
}