#!/usr/bin/perl

use warnings;
use strict;
use Postgres;

$conn = db_connect($database,$host,$port)
    or die "could not connect -- $Postgres::error";

