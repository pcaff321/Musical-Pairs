import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Button, Grid, Typography, TextField, FormHelperText, FormControl, FormControlLabel, Radio, RadioGroup} from '@material-ui/core'
import { withRouter } from './withrouter';

class CreateSurvey extends Component {
     defaultVotes = 2;

    constructor(props) {
        super(props);
        this.state = {
            guest_can_pause: true,
            votes_to_skip: this.defaultVotes,
            round_count: this.defaultVotes,
            round_list: {1: "content"}
        };
    }

    handleVotesChange = (e) => {
        this.setState({
            votes_to_skip: e.target.value
    });
    }

    handleGuestCanPauseChange = (e) => {
        this.setState({
            guest_can_pause: e.target.value === true ? true : false
        });
    }

    handleRoundCountChange = (e) => {
        this.setState({
            round_count: e.target.value
        });
    }

    handleSurveyButtonPressed = () => {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                round_count: this.state.round_count,
                round_list: this.state.round_list,
                "fuck you": "just work"
            })
        };
        fetch("/audio/createsurvey", requestOptions)
            .then((response) => response.json())
            .then((data) => this.props.navigate("/survey/" + data.code)
        );
    }

    render() {
        return (
            <Grid container spacing={1} style={{ height: "75%" }} alignItems="center" justifyContent="center">

                <Grid item xs={12} align="center">
                    <Typography component="h4" variant="h4">
                        Create a Survey
                    </Typography>
                </Grid>

                {/* <Grid item xs={12} align="center">
                    <FormControl component="fieldset">
                        <FormHelperText>
                            Guest Control of Playback State
                        </FormHelperText>
                        <RadioGroup row defaultValue="true" onChange={this.handleGuestCanPauseChange}>
                            <FormControlLabel 
                                value="true" control={<Radio color="primary" />} 
                                label="Play/Pause" labelPlacement="bottom"
                            />
                            <FormControlLabel 
                                value="false" control={<Radio color="secondary" />} 
                                label="No Control" labelPlacement="bottom"
                            />
                        </RadioGroup>
                    </FormControl>
                </Grid>

                <Grid item xs={12} align="center">
                    <FormControl>
                        <TextField 
                            required={true} type="number" defaultValue={this.defaultVotes} 
                            inputProps={{min: 1, style: {textAlign: "center"}}}
                            onChange={this.handleVotesChange}
                        />
                        <FormHelperText>
                            Votes Required to Skip Song
                        </FormHelperText>
                    </FormControl>
                </Grid> */}

                <Grid item xs={12} align="center">
                    <FormControl>
                        <TextField 
                            required={true} type="number" defaultValue={this.defaultVotes} 
                            inputProps={{min: 1, style: {textAlign: "center"}}}
                            onChange={this.handleRoundCountChange}
                        />
                        <FormHelperText>
                            Number of Rounds
                        </FormHelperText>
                    </FormControl>
                </Grid>

                <Grid item xs={12} align="center">
                    <Button color="secondary" variant="contained" onClick={this.handleSurveyButtonPressed}>
                        Create Survey
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

export default withRouter(CreateSurvey);
