// =====================================================================
// KerML v1.0 — exhaustive concrete-syntax reference model
// Every construct below is grounded in the normative spec (specs/kerml.txt)
// and the reserved-word list of section 8.2.2.6.
// Domain: a vehicle / fuel system, following the spec's own examples.
// =====================================================================


// =====================================================================
// 1. ROOT LAYER — namespaces, annotations, dependencies, imports
// =====================================================================

// --- Documentation comment attached to the root namespace -----------
doc /* Exhaustive KerML model illustrating every concrete construct. */

// --- Package: a namespace that is also a "unit" of a model ----------
package VehicleModel {

    // --- Library package (standard library units) -------------------
    // library package Units;          // 'library' + 'standard' modifiers
    // standard library package Base;  // only for normative libraries

    // --- Imports ----------------------------------------------------
    import ScalarValues::*;            // NamespaceImport  (all members)
    import ScalarValues::Real;         // MembershipImport (one member)
    import ISQ::**;                    // recursive namespace import
    public import Base::Anything;      // visibility on an import
    private import Occurrences::*;

    // --- Alias ------------------------------------------------------
    alias Num for ScalarValues::Real;

    // --- Comments ---------------------------------------------------
    comment Overview about VehicleModel
        /* Top-level model of a road vehicle and its fuel system. */

    // implicit comment: annotates the containing namespace
    /* This comment annotates VehicleModel itself. */

    // localized comment
    comment locale "fr_FR"
        /* Modele de vehicule routier. */

    // --- Textual representation (foreign notation embedded) ---------
    rep inOCL language "ocl"
        /* self.wheels->size() >= 3 */

    // --- Dependency (n-ary on both sides) ---------------------------
    dependency Traceability from VehicleModel to ScalarValues, ISQ;
    dependency from VehicleModel to Base;   // unnamed: 'from' optional

    // --- Metadata ---------------------------------------------------
    metaclass SafetyCritical;              // a Metaclass definition
    metadata SafetyCritical about Vehicle; // a MetadataFeature usage


    // =================================================================
    // 2. CORE LAYER — types, classifiers, features, specialization
    // =================================================================

    // --- Type: the most general classifiable thing ------------------
    type AnyThing specializes Base::Anything;

    // --- Abstract type (user-level abstractness, not metaclass) -----
    abstract type Measurable specializes Base::Anything;

    // --- Classifier: classifies things, no identity commitment ------
    classifier Vehicle;
    classifier Wheel;
    classifier Fuel;

    // --- Specialization (inline, keyword or symbol) -----------------
    classifier Bicycle specializes Vehicle;
    classifier Motorcycle :> Vehicle;              // ':>' = specializes

    // --- Multiple specialization ------------------------------------
    classifier HybridVehicle specializes Vehicle, Measurable;

    // --- Multiplicity on a classifier -------------------------------
    classifier MyBike   [1] specializes Bicycle;
    classifier YourBike [1] specializes Bicycle disjoint from MyBike;

    // --- Standalone Specialization / Subclassification relationships -
    specialization Super subclassifier Bicycle specializes Vehicle;
    specialization subclassifier Motorcycle :> Vehicle {
        doc /* Relationship declared as a first-class element. */
    }

    // --- Disjoining, unioning, intersecting, differencing -----------
    classifier PoweredVehicle specializes Vehicle;
    classifier PedalVehicle   specializes Vehicle;
    classifier AnyRoadVehicle specializes Vehicle
        unions PoweredVehicle, PedalVehicle;
    classifier HybridOnly     specializes Vehicle
        intersects PoweredVehicle, PedalVehicle;
    classifier PureMuscle     specializes Vehicle
        differences PedalVehicle, PoweredVehicle;
    disjoining PoweredVehicle disjoint from PedalVehicle;

    // --- Conjugation -------------------------------------------------
    classifier Port;
    classifier ConjugatedPort ~ Port;          // '~' = conjugates
    conjugation ConjugatedPort conjugates Port;

    // --- Features ---------------------------------------------------
    classifier Automobile specializes Vehicle {

        // simple feature with typing (':' = 'typed by')
        feature vin : ScalarValues::String;
        feature mass typed by ISQ::MassValue;

        // multiplicity, ordering, uniqueness
        composite feature wheels[4] : Wheel ordered;
        feature passengers[0..5] : Person nonunique;

        // direction
        in  feature fuelIn  : Fuel;
        out feature exhaust : Fuel;
        inout feature coolant : Fuel;

        // variability and constancy
        var   feature fuelLevel : Real;
        const feature wheelCount : Integer = 4;

        // derived feature with a computed value
        derived feature isEmpty = fuelLevel == 0;

        // abstract feature (must be redefined by specializations)
        abstract feature engineKind : Base::Anything;

        // reference vs composite vs portion
        composite feature tank : Tank;
        feature owner references Person;           // '::>' = references
        portion feature frontHalf : Automobile;

        // end feature (participates in a connector/association)
        end feature driverSeat : Seat;

        // default value
        feature color : ScalarValues::String default "white";

        // feature chaining
        feature tankCapacity : Real chains tank.capacity;

        // feature value binding
        feature nominalPressure : Real = 2.4;
    }

    classifier Person;
    classifier Seat;

    // --- Subsetting / redefinition across a hierarchy ---------------
    classifier WheeledVehicle specializes Vehicle {
        composite feature wheels[1..*] : Wheel;
    }
    classifier MotorizedVehicle specializes WheeledVehicle {
        composite feature redefines wheels[2..4];     // ':>>' = redefines
    }
    classifier FourWheeler specializes MotorizedVehicle {
        composite feature :>> wheels[4] : DriveWheel;
    }
    classifier DriveWheel specializes Wheel;

    // --- Subsetting -------------------------------------------------
    classifier Fleet {
        feature allVehicles[*] : Vehicle;
        feature electricOnes[*] : Vehicle subsets allVehicles;
        feature firstOne : Vehicle :> allVehicles;    // ':>' = subsets
    }

    // --- Standalone Subsetting / Redefinition / Typing relationships -
    subset Fleet::electricOnes subsets Fleet::allVehicles;
    redefinition MotorizedVehicle::wheels :>> WheeledVehicle::wheels;
    typing Automobile::vin typed by ScalarValues::String;

    // --- Inverting and featuring ------------------------------------
    inverse Automobile::owner of Person::ownedVehicle;
    inverting inverse Automobile::owner of Person::ownedVehicle;
    featuring Automobile::vin featured by Automobile;

    // --- Crossing (cross-subsetting on end features) ----------------
    classifier Ownership {
        end feature theOwner  : Person;
        end feature theCar    : Automobile;
    }

    // --- Multiplicity as a first-class element ----------------------
    multiplicity wheelRange [1..*];

    // --- Filter -----------------------------------------------------
    package ElectricOnly {
        import VehicleModel::*;
        filter @SafetyCritical;
    }


    // =================================================================
    // 3. KERNEL LAYER — classes, structures, associations, behaviors
    // =================================================================

    // --- DataType: no identity, distinguished only by feature values -
    datatype Color {
        feature red   : Integer;
        feature green : Integer;
        feature blue  : Integer;
    }

    // --- Class: has identity, exists in time -------------------------
    class Engine {
        feature displacement : Real;
        feature serial : ScalarValues::String;
    }

    // --- Structure: a Class that is primarily structural -------------
    struct Tank {
        feature capacity : Real;
        var feature contents : Fuel;
    }

    // --- Association: a Relationship that is also a Classifier -------
    assoc Owns {
        end feature owner : Person[0..1];
        end feature owned : Automobile[*];
    }

    // --- Association structure (Association + Structure) -------------
    assoc struct Registration {
        feature plate : ScalarValues::String;
        end feature holder  : Person;
        end feature vehicle : Automobile;
    }

    // --- Connector: a usage of an Association ------------------------
    classifier Garage {
        feature aPerson : Person;
        feature aCar    : Automobile;

        connector ownership : Owns from aPerson to aCar;
        connector [1] from aPerson to aCar;          // with multiplicity
    }

    // --- Binding connector -------------------------------------------
    classifier Calibration {
        feature measured : Real;
        feature expected : Real;
        binding calib = measured = expected;
        binding of measured = expected;
    }

    // --- Succession (ordering of occurrences) -------------------------
    classifier Startup {
        feature ignition : Occurrences::Occurrence;
        feature running  : Occurrences::Occurrence;
        succession first ignition then running;
    }

    // --- Behavior and Step ---------------------------------------------
    behavior Drive {
        in  feature route    : ScalarValues::String;
        out feature arrived  : ScalarValues::Boolean;

        step accelerate : Accelerate;
        step brake      : Brake;
        succession first accelerate then brake;
    }
    behavior Accelerate;
    behavior Brake;

    // --- Function and Expression ---------------------------------------
    function Add {
        in feature a : Real;
        in feature b : Real;
        return feature result : Real;
    }

    expr sum2 : Add { in a = 1.0; in b = 2.0; }

    // --- Predicate, Boolean expression, Invariant ----------------------
    predicate IsRoadworthy {
        in feature v : Automobile;
        return feature ok : ScalarValues::Boolean;
    }

    bool roadworthy : IsRoadworthy { in v = someCar; }

    inv tankNotOverfilled { Tank::contents <= Tank::capacity }
    inv not emptyTank { Tank::capacity > 0 }      // negated invariant

    // --- Interaction: an Association that is also a Behavior ------------
    interaction Refueling {
        end feature station : Tank;
        end feature vehicle : Automobile;
        step transfer : Drive;
    }

    // --- Flow and Succession flow ----------------------------------------
    classifier FuelSystem {
        feature pump : Tank;
        feature eng  : Engine;

        flow of Fuel from pump.contents to eng.displacement;
        succession flow of Fuel from pump.contents to eng.displacement;
    }

    // --- Metaclass and metadata usage --------------------------------------
    metaclass Certification {
        feature authority : ScalarValues::String;
    }
    metadata Certification about Automobile {
        authority = "UTAC";
    }

    // --- Visibility modifiers -----------------------------------------------
    package Internals {
        private feature secretKey : ScalarValues::String;
        protected feature sharedKey : ScalarValues::String;
        public feature publicId : ScalarValues::String;
    }

    // --- Member (explicit membership with alias) ----------------------------
    package Exports {
        member alias Car for VehicleModel::Automobile;
    }


    // =================================================================
    // 4. EXPRESSION SUBLANGUAGE
    // =================================================================

    classifier Expressions {
        feature a : Real = 1.0;
        feature b : Real = 2.0;
        feature flag : ScalarValues::Boolean = true;

        // arithmetic
        feature e1 : Real = a + b * 2 - 1 / 2 ** 3;

        // comparison and equality
        feature e2 : ScalarValues::Boolean = a < b;
        feature e3 : ScalarValues::Boolean = a == b;      // value equality
        feature e4 : ScalarValues::Boolean = a === b;     // identity equality
        feature e5 : ScalarValues::Boolean = a != b;

        // logical (and/or/xor/not, implies)
        feature e6 : ScalarValues::Boolean = flag and not flag;
        feature e7 : ScalarValues::Boolean = flag or flag xor flag;
        feature e8 : ScalarValues::Boolean = flag implies flag;

        // conditional
        feature e9 : Real = if flag ? a else b;

        // null-coalescing and null test
        feature e10 : Real = a ?? b;
        feature e11 : ScalarValues::Boolean = a == null;

        // classification tests
        feature e12 : ScalarValues::Boolean = a istype Real;
        feature e13 : ScalarValues::Boolean = a hastype Real;
        feature e14 : ScalarValues::Boolean = a @ SafetyCritical;
        feature e15 : Real = a as Real;
        feature e16 : ScalarValues::Boolean = a meta Real;

        // collections, ranges, indexing, chaining
        feature list[*] : Real = (1.0, 2.0, 3.0);
        feature range[*] : Integer = 1..10;
        feature picked : Real = list#(1);
        feature chainAccess : Real = someCar.tank.capacity;

        // quantification over a collection
        feature allPositive : ScalarValues::Boolean =
            list->forAll{ in x : Real; x > 0 };
        feature anyPositive : ScalarValues::Boolean =
            list->exists{ in x : Real; x > 0 };
        feature doubled[*] : Real =
            list->collect{ in x : Real; x * 2 };
        feature bigOnes[*] : Real =
            list->select{ in x : Real; x > 1 };
    }

    feature someCar : Automobile;
}
