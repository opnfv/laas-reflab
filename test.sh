#!/bin/bash

function lint {
    echo "######################################################"
    echo "##                 Running Linters                  ##"
    echo "######################################################"

    local status=0

    echo "========================="
    echo "          flake8         "
    echo "========================="
    find . -name "*.py" -print0 | xargs -0 flake8

    (( status = status + "$?" ))

    echo ""
    echo "========================="
    echo "         yamllint        "
    echo "========================="
    
    find . -name "*.yaml" -print0 | xargs -0 yamllint

    (( status = status + "$?" ))

    echo ""
    echo "========================="
    echo "       shellcheck        "
    echo "========================="
    find . -name "*.sh" -print0 | xargs -0 shellcheck

    (( status = status + "$?" ))

    exit "$status"
}



lint

