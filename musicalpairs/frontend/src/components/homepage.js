import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Button, Grid, Typography } from '@material-ui/core'

export default class HomePage extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Grid container spacing={1} style={{ height: "75%" }} alignItems="center" justifyContent="center">
                <Grid item xs={12} align="center">
                    <Typography component="h4" variant="h4">
                        Home Page
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <Button color="primary" variant="contained" to="/create" component={Link}>
                        Create a Survey
                    </Button>
                </Grid>
            </Grid>
        )
    }
}