import requests
import json
import re
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from enum import Enum


class TransportCategory(str, Enum):
    """Transport category options for bookings."""
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    EMPTY_PICKUP = "EMPTY_PICKUP"
    EMPTY_RETURN = "EMPTY_RETURN"
    ROUND_TRIP = "ROUND_TRIP"


class LoadStatus(str, Enum):
    """Load status options for containers."""
    EMPTY = "EMPTY"
    FULL = "FULL"


class LoadingPointType(str, Enum):
    """Types of loading points in a route."""
    WAREHOUSE = "WAREHOUSE"
    WEIGHING_STATION = "WEIGHING_STATION"
    SEAPORT_TERMINAL = "SEAPORT_TERMINAL"
    RAILWAY_TERMINAL = "RAILWAY_TERMINAL"
    CUSTOMS_OFFICE = "CUSTOMS_OFFICE"
    CONTAINER_DEPOT = "CONTAINER_DEPOT"
    VETERINARY_OFFICE = "VETERINARY_OFFICE"


class ContainerServiceType(str, Enum):
    """Types of container services that can be added."""
    ACTIVE_COOLING = "ACTIVE_COOLING"
    CUSTOMS_CLEARANCE = "CUSTOMS_CLEARANCE"
    EXPORT_CUSTOMS = "EXPORT_CUSTOMS"
    IMPORT_CUSTOMS = "IMPORT_CUSTOMS"
    VETERINARY_CONTROL = "VETERINARY_CONTROL"
    VET_STOP = "VET_STOP"
    EXTRA_STORAGE_DAY_20 = "EXTRA_STORAGE_DAY_20"
    EXTRA_STORAGE_DAY_40 = "EXTRA_STORAGE_DAY_40"
    HANDLING_DEPOT = "HANDLING_DEPOT"
    CUSTODIAN_CHANGE = "CUSTODIAN_CHANGE"
    CHANGE_FEE_1 = "CHANGE_FEE_1"
    CHANGE_FEE_2 = "CHANGE_FEE_2"
    CHANGE_FEE_3 = "CHANGE_FEE_3"
    CHANGE_FEE_4 = "CHANGE_FEE_4"
    CHANGE_FEE_5 = "CHANGE_FEE_5"
    CHASSIS_RENTAL = "CHASSIS_RENTAL"
    # Add ADR types as mentioned in changelog 3.1.0


class SolasMethod(str, Enum):
    """SOLAS verification methods."""
    WEIGHING = "WEIGHING"
    CALCULATION = "CALCULATION"


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
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
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
    
    # Validation methods
    def _validate_job_order_ref(self, job_order_ref: str) -> bool:
        """
        Validate job order reference format.
        
        Args:
            job_order_ref: The job order reference to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not job_order_ref or len(job_order_ref) > 128:
            raise ValueError("Job order reference must be between 1 and 128 characters")
        return True
    
    def _validate_container_number(self, container_number: str) -> bool:
        """
        Validate container number format (ISO 6346).
        
        Args:
            container_number: The container number to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Basic validation for container number format - 11 characters
        # For a complete ISO 6346 validation, we'd need more complex logic
        if not container_number or len(container_number) != 11:
            raise ValueError("Container number must be exactly 11 characters")
        return True
    
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
        return True
    
    def _validate_weight(self, weight: int) -> bool:
        """
        Validate container weight.
        
        Args:
            weight: The weight in kg to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        if weight < 0:
            raise ValueError("Weight cannot be negative")
        return True
    
    def _validate_net_weight(self, weight: int) -> bool:
        """
        Validate container net weight.
        
        Args:
            weight: The net weight in kg to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        if weight < 0 or weight > 35000:
            raise ValueError("Net weight must be between 0 and 35000 kg")
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
    
    # API Methods
    def create_booking(self, booking_data: Dict) -> Dict:
        """
        Create a new booking.
        
        Args:
            booking_data: Dictionary containing booking information
            
        Returns:
            API response with created booking details
        """
        # Validate the booking data
        self._validate_booking_data(booking_data)
        
        return self._make_request("POST", "/bookings", data=booking_data)
    
    def get_booking(self, job_order_ref: str) -> Dict:
        """
        Get a booking by job order reference.
        
        Args:
            job_order_ref: Job order reference
            
        Returns:
            Booking details
        """
        self._validate_job_order_ref(job_order_ref)
        
        return self._make_request("GET", f"/bookings/{job_order_ref}")
    
    def update_booking(self, job_order_ref: str, booking_data: Dict, if_match: str) -> Dict:
        """
        Update an existing booking.
        
        Args:
            job_order_ref: Job order reference
            booking_data: Updated booking data
            if_match: ETag for optimistic locking
            
        Returns:
            Updated booking details
        """
        self._validate_job_order_ref(job_order_ref)
        self._validate_booking_data(booking_data)
        
        if not if_match:
            raise ValueError("If-Match header is required for booking updates")
        
        return self._make_request(
            "PUT", 
            f"/bookings/{job_order_ref}", 
            data=booking_data,
            if_match=if_match
        )
    
    def cancel_containers(
        self, 
        job_order_ref: str, 
        container_numbers: Optional[List[str]] = None,
        container_sequence_numbers: Optional[List[int]] = None,
        if_match: str = None
    ) -> Dict:
        """
        Cancel containers for a booking.
        
        Args:
            job_order_ref: Job order reference
            container_numbers: List of container numbers to cancel
            container_sequence_numbers: List of container sequence numbers to cancel
            if_match: ETag for optimistic locking
            
        Returns:
            Cancellation details
        """
        self._validate_job_order_ref(job_order_ref)
        
        if container_numbers:
            for number in container_numbers:
                self._validate_container_number(number)
                
        if container_sequence_numbers:
            for number in container_sequence_numbers:
                if number < 0:
                    raise ValueError("Container sequence numbers must be non-negative")
        
        params = {}
        if container_numbers:
            params['container_numbers'] = container_numbers
        if container_sequence_numbers:
            params['container_sequence_numbers'] = container_sequence_numbers
            
        if not if_match:
            raise ValueError("If-Match header is required for container cancellation")
        
        return self._make_request(
            "DELETE", 
            f"/bookings/{job_order_ref}/containers", 
            params=params,
            if_match=if_match
        )
    
    def get_booking_status(self, job_order_ref: str) -> Dict:
        """
        Get booking status by job order reference.
        
        Args:
            job_order_ref: Job order reference
            
        Returns:
            Booking status details
        """
        self._validate_job_order_ref(job_order_ref)
        
        return self._make_request("GET", f"/bookings/{job_order_ref}/status")
    
    def create_price_quotation(self, quotation_data: Dict) -> Dict:
        """
        Create a non-binding price quotation.
        
        Args:
            quotation_data: Dictionary with route and container information
            
        Returns:
            Price quotation details
        """
        self._validate_quotation_data(quotation_data)
        
        return self._make_request("POST", "/quotations", data=quotation_data)
    
    def _validate_booking_data(self, booking_data: Dict) -> bool:
        """
        Validate booking data structure and values.
        
        Args:
            booking_data: Booking data to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        if 'booking' not in booking_data:
            raise ValueError("Booking data must contain a 'booking' field")
            
        booking = booking_data['booking']
        
        # Validate required fields
        if 'transport_category' not in booking:
            raise ValueError("Booking must specify a transport category")
        elif booking['transport_category'] not in [e.value for e in TransportCategory]:
            raise ValueError(f"Invalid transport category: {booking['transport_category']}")
            
        if 'load_status' not in booking:
            raise ValueError("Booking must specify a load status")
        elif booking['load_status'] not in [e.value for e in LoadStatus]:
            raise ValueError(f"Invalid load status: {booking['load_status']}")
        
        # Validate containers
        if 'containers' not in booking_data or not booking_data['containers']:
            raise ValueError("Booking must contain at least one container")
            
        for container in booking_data['containers']:
            self._validate_container_data(container)
            
        return True
    
    def _validate_container_data(self, container: Dict) -> bool:
        """
        Validate container data structure and values.
        
        Args:
            container: Container data to validate
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Validate required fields
        required_fields = ['sequence_number', 'type_code']
        
        for field in required_fields:
            if field not in container:
                raise ValueError(f"Container must specify {field}")
                
        # Validate fields
        if 'sequence_number' in container and container['sequence_number'] < 0:
            raise ValueError("Container sequence number must be non-negative")
            
        if 'type_code' in container:
            self._validate_iso_code(container['type_code'])
            
        if 'provision_at' in container:
            self._validate_date_time(container['provision_at'])
            
        if 'assumed_net_weight' in container:
            self._validate_net_weight(container['assumed_net_weight'])
            
        if 'assumed_tara' in container:
            self._validate_weight(container['assumed_tara'])
            
        # Validate services
        if 'services' in container and container['services']:
            for service in container['services']:
                if 'type' not in service:
                    raise ValueError("Container service must specify a type")
                    
                try:
                    ContainerServiceType(service['type'])
                except ValueError:
                    raise ValueError(f"Invalid container service type: {service['type']}")
                    
                if 'quantity' in service and (not isinstance(service['quantity'], int) or service['quantity'] <= 0):
                    raise ValueError("Container service quantity must be a positive integer")
                    
        return True
    
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