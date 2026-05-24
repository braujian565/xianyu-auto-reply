#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xianyu Auto Reply - Backend Web Service
Main entry point for the FastAPI application.

This service handles:
- WebSocket connections for real-time messaging
- REST API endpoints for configuration management
- Integration with Xianyu (Idle Fish) platform
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Starting Xianyu Auto Reply backend service...")
    # TODO: Initialize database connections, background tasks, etc.
    yield
    logger.info("Shutting down Xianyu Auto Reply backend service...")
    # TODO: Clean up resources


# Initialize FastAPI application
app = FastAPI(
    title="Xianyu Auto Reply API",
    description="Backend service for automated replies on Xianyu (Idle Fish) platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - service health check."""
    return {
        "status": "ok",
        "service": "xianyu-auto-reply",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "components": {
            "api": "ok",
        },
    }


# Import and register routers
# These will be added as the project grows
# from routers import auth, messages, config
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
# app.include_router(config.router, prefix="/api/config", tags=["Configuration"])


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    logger.info(f"Starting server on {host}:{port} (debug={debug})")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
