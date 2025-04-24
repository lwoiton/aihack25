import requests
import json
import re
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from enum import Enum

class LoadingPointType(str, Enum):
    """Types of loading points in a route."""
    WAREHOUSE = "WAREHOUSE"
    WEIGHING_STATION = "WEIGHING_STATION"
    SEAPORT_TERMINAL = "SEAPORT_TERMINAL"
    RAILWAY_TERMINAL = "RAILWAY_TERMINAL"
    CUSTOMS_OFFICE = "CUSTOMS_OFFICE"
    CONTAINER_DEPOT = "CONTAINER_DEPOT"
    VETERINARY_OFFICE = "VETERINARY_OFFICE"

class DriveMyBoxAPIException(Exception):
    """Custom exception for DriveMyBox API errors."""
    def __init__(self, status_code: int, message: str, details: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"API Error ({status_code}): {message}")


class DriveMyBoxClient:
    """
    Client for interacting with the driveMybox API.
    
    This class provides methods to create, update, and manage bookings,
    as well as request quotations for container transport services.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.drivemybox.de", customer_id: Optional[str] = None):
        """
        Initialize the DriveMyBox API client.
        
        Args:
            api_key: The API key for authentication
            base_url: Base URL for the API (defaults to production URL)
            customer_id: Optional customer ID for authentication
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.customer_id = customer_id
        
    def _get_headers(self, if_match: Optional[str] = None) -> Dict[str, str]:
        """
        Get request headers with authentication.
        
        Args:
            if_match: Optional ETag for optimistic locking
            
        Returns:
            Dictionary of headers
        """
        print(self.api_key)
        headers = {
			"x-api-key" : self.api_key,
			"Content-Type": "application/json"
		}
        
        if self.customer_id:
            headers['x-customer-id'] = self.customer_id
            
        if if_match:
            headers['If-Match'] = if_match
            
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None, if_match: Optional[str] = None) -> Dict:
        """
        Make a request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request payload
            params: Query parameters
            if_match: ETag for optimistic locking
            
        Returns:
            API response as dictionary
            
        Raises:
            DriveMyBoxAPIException: If the API returns an error
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers(if_match)
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )
            
            # Store ETag for later use if present
            etag = response.headers.get('ETag')
            if etag:
                self.last_etag = etag
                
            # Check for errors
            if response.status_code >= 400:
                try:
                    error_details = response.json()
                except:
                    error_details = {"raw": response.text}
                    
                raise DriveMyBoxAPIException(
                    status_code=response.status_code,
                    message=f"API request failed: {response.reason}",
                    details=error_details
                )
                
            # Parse the response
            if response.content:
                return response.json()
            return {}
            
        except requests.RequestException as e:
            raise DriveMyBoxAPIException(
                status_code=500,
                message=f"Request failed: {str(e)}"
            )
    
    def _validate_iso_code(self, iso_code: str) -> bool:
        """
        Validate container ISO code.
        
        Args:
            iso_code: The ISO code to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not iso_code or len(iso_code) > 4:
            raise ValueError("ISO code must be at most 4 characters")
        if iso_code not in ['22B0','22G1','22R1','22TD','22TG','22TN','22U1','22U6','22V0','25G1','25R1','25U1','25U6','2CG1','42B0','42G1','42R1','42TD','42TG','42TN','42U1','42U6','42V0','45G1','45R1','45U1','45U6','4CG1','4EG1','L5G1','L5R1','LEG1']:
            raise ValueError("ISO type code {iso_code} not supported by ISO 6346 and therefore not supported by the API.")
        return True

    def _validate_address(self, address: Dict) -> bool:
        """
        Validate address information.
        
        Args:
            address: Address dictionary to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Check for geographic coordinates
        has_geo = 'geo_coordinates' in address and 'latitude' in address['geo_coordinates'] and 'longitude' in address['geo_coordinates']
        
        # Check for traditional address fields
        has_address_fields = all(key in address for key in ['city', 'country', 'postal_code'])
        
        if not (has_geo or has_address_fields):
            raise ValueError("Address must contain either geographic coordinates or city, country, and postal code")
        
        return True
    
    def _validate_date_time(self, dt_str: str) -> bool:
        """
        Validate datetime string format (RFC 3339).
        
        Args:
            dt_str: Datetime string to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        try:
            # Try to parse the datetime
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            raise ValueError("Datetime must be in RFC 3339 format (e.g., 2021-01-31T12:30:25Z)")
    

    def create_price_quotation(self, quotation_data: Dict) -> Dict:
        """
        Create a non-binding price quotation.
        
        Args:
            quotation_data: Dictionary with route and container information
            
        Returns:
            Price quotation details
        """
        self._validate_quotation_data(quotation_data)
        
        return self._make_request("POST", "/booking/quotations", data=quotation_data)
    
    
    def _validate_quotation_data(self, quotation_data: Dict) -> bool:
        """
        Validate quotation data structure and values.
        
        Args:
            quotation_data: Quotation data to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        if 'route' not in quotation_data:
            raise ValueError("Quotation data must contain a 'route' field")
            
        if 'route_loading_points' not in quotation_data['route'] or not quotation_data['route']['route_loading_points']:
            raise ValueError("Route must contain at least one loading point")
            
        # Validate route loading points
        provision_locations = 0
        for point in quotation_data['route']['route_loading_points']:
            if 'type' not in point:
                raise ValueError("Loading point must specify a type")
                
            try:
                LoadingPointType(point['type'])
            except ValueError:
                raise ValueError(f"Invalid loading point type: {point['type']}")
                
            if 'sequence_number' not in point:
                raise ValueError("Loading point must specify a sequence number")
                
            if point['sequence_number'] < 0:
                raise ValueError("Loading point sequence number must be non-negative")
                
            if 'address' not in point:
                raise ValueError("Loading point must specify an address")
                
            self._validate_address(point['address'])
            
            # Count provision locations
            if 'provision_location' in point and point['provision_location']:
                provision_locations += 1
                
        if provision_locations > 1:
            raise ValueError("Route can have at most one provision location")
            
        # Validate containers
        if 'containers' not in quotation_data or not quotation_data['containers']:
            raise ValueError("Quotation must contain at least one container")
            
        for container in quotation_data['containers']:
            if 'sequence_number' not in container:
                raise ValueError("Container must specify a sequence number")
                
            if container['sequence_number'] < 0:
                raise ValueError("Container sequence number must be non-negative")
                
            if 'type_code' not in container:
                raise ValueError("Container must specify a type code")
                
            self._validate_iso_code(container['type_code'])
            
            if 'provision_at' not in container:
                raise ValueError("Container must specify a provision date")
                
            self._validate_date_time(container['provision_at'])
                
        return True